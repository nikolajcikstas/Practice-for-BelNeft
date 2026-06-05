import { Alert, Button, DatePicker, Form, Input, Modal, Spin, Typography, message } from "antd";
import dayjs, { Dayjs } from "dayjs";
import "dayjs/locale/ru";
import updateLocale from "dayjs/plugin/updateLocale";
import { useEffect, useState } from "react";
import { Calendar, dayjsLocalizer } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import client from "../api/client";
import type { Booking } from "../api/types";

const WEEKDAYS_SHORT = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];

dayjs.extend(updateLocale);
dayjs.updateLocale("ru", {
  weekdaysShort: WEEKDAYS_SHORT,
  weekdaysMin: WEEKDAYS_SHORT,
});
dayjs.locale("ru");
const localizer = dayjsLocalizer(dayjs);

const calendarFormats = {
  weekdayFormat: (date: Date) => WEEKDAYS_SHORT[dayjs(date).day()],
  dayHeaderFormat: (date: Date) =>
    `${WEEKDAYS_SHORT[dayjs(date).day()]} ${dayjs(date).format("DD.MM")}`,
};

const { Title } = Typography;
const { RangePicker } = DatePicker;

interface CalEvent {
  id: number;
  title: string;
  start: Date;
  end: Date;
  resource: Booking;
}

export default function BookingPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [modalOpen, setModalOpen] = useState(false);
  const [slotRange, setSlotRange] = useState<[Dayjs, Dayjs] | null>(null);
  const [form] = Form.useForm();

  const loadDay = (date: Date) => {
    setLoading(true);
    const dateStr = dayjs(date).format("YYYY-MM-DD");
    client
      .get<Booking[]>(`/bookings?date=${dateStr}`)
      .then((r) => {
        setBookings(r.data);
        setError(null);
      })
      .catch(() => setError("Не удалось загрузить бронирования"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadDay(currentDate); }, []);

  const events: CalEvent[] = bookings.map((b) => ({
    id: b.id,
    title: b.topic,
    start: new Date(b.start_time),
    end: new Date(b.end_time),
    resource: b,
  }));

  const handleSelectSlot = ({ start, end }: { start: Date; end: Date }) => {
    setSlotRange([dayjs(start), dayjs(end)]);
    form.resetFields();
    form.setFieldsValue({ range: [dayjs(start), dayjs(end)] });
    setModalOpen(true);
  };

  const handleCreate = async () => {
    const values = await form.validateFields();
    const [start, end] = values.range as [Dayjs, Dayjs];
    try {
      await client.post("/bookings", {
        employee_id: 1,
        topic: values.topic,
        start_time: start.toISOString(),
        end_time: end.toISOString(),
      });
      message.success("Переговорная забронирована");
      setModalOpen(false);
      loadDay(currentDate);
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
        loadDay(currentDate);
      },
    });
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>Переговорная</Title>
        <Button type="primary" onClick={() => { setSlotRange(null); form.resetFields(); setModalOpen(true); }}>
          + Забронировать
        </Button>
      </div>

      {error && <Alert type="error" message={error} style={{ marginBottom: 12 }} />}
      {loading && <Spin />}

      <Calendar
        localizer={localizer}
        formats={calendarFormats}
        events={events}
        defaultView="day"
        views={["month", "week", "day"]}
        step={30}
        timeslots={2}
        date={currentDate}
        onNavigate={(date) => { setCurrentDate(date); loadDay(date); }}
        selectable
        onSelectSlot={handleSelectSlot}
        onSelectEvent={handleCancel}
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
