import { Alert, Button, DatePicker, Form, Input, Modal, Spin, Typography, message } from "antd";
import dayjs, { Dayjs } from "dayjs";
import "dayjs/locale/ru";
import isoWeek from "dayjs/plugin/isoWeek";
import updateLocale from "dayjs/plugin/updateLocale";
import { useCallback, useEffect, useState } from "react";
import { Calendar, dayjsLocalizer, View } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import client from "../api/client";
import type { Booking } from "../api/types";
import EmployeeAvatar from "../components/EmployeeAvatar";
import { formatDayHeader, parseLocalDateTime, toLocalDateTimeString } from "../utils/datetime";

dayjs.extend(isoWeek);
dayjs.extend(updateLocale);
dayjs.updateLocale("ru", {
  weekStart: 1,
  weekdaysMin: ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
  weekdaysShort: ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
});
dayjs.locale("ru");

const localizer = dayjsLocalizer(dayjs);

const { Title } = Typography;
const { RangePicker } = DatePicker;

interface CalEvent {
  id: number;
  title: string;
  start: Date;
  end: Date;
  resource: Booking;
}

const calendarFormats = {
  dayFormat: (date: Date) => formatDayHeader(date),
  weekdayFormat: (date: Date) => formatDayHeader(date),
  dayHeaderFormat: (date: Date) => formatDayHeader(date),
  dayRangeHeaderFormat: ({ start, end }: { start: Date; end: Date }) =>
    `${dayjs(start).format("D MMMM")} – ${dayjs(end).format("D MMMM")}`,
  monthHeaderFormat: (date: Date) => dayjs(date).format("MMMM YYYY"),
};

function EventContent({ event }: { event: CalEvent }) {
  const b = event.resource;
  const nameParts = (b.employee_name ?? "").split(" ");
  const lastName = nameParts[0] ?? "";
  const firstName = nameParts.slice(1).join(" ") || lastName;

  return (
    <div className="booking-event">
      {b.employee_name && (
        <EmployeeAvatar
          size={22}
          employee={{
            first_name: firstName,
            last_name: lastName,
            photo_url: b.employee_photo_url,
          }}
        />
      )}
      <span className="booking-event-title">{event.title}</span>
    </div>
  );
}

export default function BookingPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [currentView, setCurrentView] = useState<View>("week");
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const loadBookings = useCallback((date: Date, view: View) => {
    setLoading(true);
    const d = dayjs(date);
    let url: string;

    if (view === "week") {
      const from = d.startOf("isoWeek").format("YYYY-MM-DD");
      const to = d.endOf("isoWeek").format("YYYY-MM-DD");
      url = `/bookings?from_date=${from}&to_date=${to}`;
    } else if (view === "month") {
      const from = d.startOf("month").format("YYYY-MM-DD");
      const to = d.endOf("month").format("YYYY-MM-DD");
      url = `/bookings?from_date=${from}&to_date=${to}`;
    } else {
      url = `/bookings?date=${d.format("YYYY-MM-DD")}`;
    }

    client
      .get<Booking[]>(url)
      .then((r) => {
        setBookings(r.data);
        setError(null);
      })
      .catch(() => setError("Не удалось загрузить бронирования"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadBookings(currentDate, currentView);
  }, [currentDate, currentView, loadBookings]);

  const events: CalEvent[] = bookings.map((b) => ({
    id: b.id,
    title: b.topic,
    start: parseLocalDateTime(b.start_time),
    end: parseLocalDateTime(b.end_time),
    resource: b,
  }));

  const openCreateModal = (start?: Dayjs, end?: Dayjs) => {
    form.resetFields();
    const rangeStart = start ?? dayjs().hour(14).minute(0).second(0);
    const rangeEnd = end ?? dayjs().hour(15).minute(0).second(0);
    form.setFieldsValue({ range: [rangeStart, rangeEnd] });
    setModalOpen(true);
  };

  const handleSelectSlot = ({ start, end }: { start: Date; end: Date }) => {
    openCreateModal(dayjs(start), dayjs(end));
  };

  const handleCreate = async () => {
    const values = await form.validateFields();
    const [start, end] = values.range as [Dayjs, Dayjs];
    try {
      await client.post("/bookings", {
        employee_id: 1,
        topic: values.topic,
        start_time: toLocalDateTimeString(start),
        end_time: toLocalDateTimeString(end),
      });
      message.success("Переговорная забронирована");
      setModalOpen(false);
      loadBookings(currentDate, currentView);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosErr.response?.status === 409) {
        message.error(axiosErr.response.data?.detail ?? "Слот уже занят");
      } else {
        message.error("Ошибка при создании бронирования");
      }
    }
  };

  const handleCancel = (event: CalEvent) => {
    Modal.confirm({
      title: `Отменить бронирование «${event.title}»?`,
      okType: "danger",
      onOk: async () => {
        await client.delete(`/bookings/${event.id}`);
        message.success("Бронирование отменено");
        loadBookings(currentDate, currentView);
      },
    });
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>Переговорная</Title>
        <Button type="primary" onClick={() => openCreateModal()}>
          + Забронировать
        </Button>
      </div>

      {error && <Alert type="error" message={error} style={{ marginBottom: 12 }} />}
      {loading && <Spin style={{ marginBottom: 8 }} />}

      <Calendar
        localizer={localizer}
        culture="ru"
        events={events}
        defaultView="week"
        view={currentView}
        views={["month", "week", "day"]}
        step={30}
        timeslots={2}
        date={currentDate}
        formats={calendarFormats}
        onNavigate={(date) => setCurrentDate(date)}
        onView={(view) => setCurrentView(view)}
        selectable
        onSelectSlot={handleSelectSlot}
        onSelectEvent={handleCancel}
        components={{ event: EventContent }}
        messages={{
          today: "Сегодня",
          previous: "Назад",
          next: "Вперёд",
          month: "Месяц",
          week: "Неделя",
          day: "День",
          noEventsInRange: "Нет бронирований",
        }}
        style={{ height: 600 }}
      />

      <Modal
        title="Забронировать переговорную"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={handleCreate}
        okText="Забронировать"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="topic" label="Тема встречи" rules={[{ required: true, message: "Укажите тему" }]}>
            <Input />
          </Form.Item>
          <Form.Item name="range" label="Начало и конец" rules={[{ required: true, message: "Выберите время" }]}>
            <RangePicker showTime format="DD.MM.YYYY HH:mm" style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
