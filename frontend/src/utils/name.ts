export function formatFullName(emp: {
  last_name: string;
  first_name: string;
  middle_name: string;
}): string {
  return [emp.last_name, emp.first_name, emp.middle_name].join(" ");
}

export function formatPosition(position: string | null | undefined): string {
  const value = position?.trim();
  return value ? value : "—";
}
