import { Avatar } from "antd";
import type { Employee } from "../api/types";

type Props = {
  employee: Pick<Employee, "first_name" | "last_name" | "photo_url">;
  size?: number;
};

function initials(first: string, last: string): string {
  return `${last.charAt(0)}${first.charAt(0)}`.toUpperCase();
}

export default function EmployeeAvatar({ employee, size = 36 }: Props) {
  const label = initials(employee.first_name, employee.last_name);

  return (
    <Avatar
      size={size}
      src={employee.photo_url || undefined}
      style={{ backgroundColor: employee.photo_url ? undefined : "#1677ff", flexShrink: 0 }}
    >
      {label}
    </Avatar>
  );
}
