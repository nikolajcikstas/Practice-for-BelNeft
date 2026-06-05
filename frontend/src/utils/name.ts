export function formatFullName(emp: {
  last_name: string;
  first_name: string;
  middle_name?: string | null;
}): string {
  return [emp.last_name, emp.first_name, emp.middle_name].filter(Boolean).join(" ");
}
