import dayjs, { Dayjs } from "dayjs";

export function toLocalDateTimeString(value: Dayjs): string {
  return value.format("YYYY-MM-DDTHH:mm:ss");
}

export function parseLocalDateTime(value: string): Date {
  return dayjs(value).toDate();
}

export const WEEKDAYS_SHORT = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];

export function formatDayHeader(date: Date): string {
  const d = dayjs(date);
  return `${d.format("DD")} ${WEEKDAYS_SHORT[d.day()]}`;
}
