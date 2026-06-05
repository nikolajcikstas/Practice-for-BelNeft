import { Alert, Grid, Space, Spin, Table, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import client from "../api/client";
import type { Employee, Skill } from "../api/types";
import EmployeeAvatar from "../components/EmployeeAvatar";

const { Title } = Typography;
const { useBreakpoint } = Grid;

const LEVEL_COLORS: Record<number, string> = {
  0: "#d9d9d9",
  1: "#ffc069",
  2: "#ffd591",
  3: "#ffe58f",
  4: "#95de64",
  5: "#52c41a",
};

export default function SkillsMatrixPage() {
  const screens = useBreakpoint();
  const isMobile = !screens.md;
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      client.get<{ items: Employee[] }>("/employees?size=100"),
      client.get<Skill[]>("/skills"),
    ])
      .then(([empRes, skillRes]) => {
        setEmployees(empRes.data.items);
        setSkills(skillRes.data);
      })
      .catch(() => setError("Не удалось загрузить данные"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" className="page-spinner" />;
  if (error) return <Alert type="error" message={error} />;

  const skillColumns = skills.map((skill) => ({
    title: (
      <div className="matrix-skill-header" style={{ textAlign: "center", fontSize: 12 }}>
        <div style={{ fontWeight: 600 }}>{skill.name}</div>
        <Tag color="blue" style={{ fontSize: 10 }}>{skill.category}</Tag>
      </div>
    ),
    key: `skill_${skill.id}`,
    width: isMobile ? 56 : 110,
    render: (_: unknown, emp: Employee) => {
      const es = emp.skills.find((s) => s.skill_id === skill.id);
      const level = es?.proficiency_level ?? 0;
      return (
        <div
          style={{
            background: LEVEL_COLORS[level],
            borderRadius: 4,
            padding: "4px 0",
            textAlign: "center",
            fontWeight: 600,
            fontSize: isMobile ? 11 : 13,
          }}
        >
          {level === 0 ? "—" : level}
        </div>
      );
    },
  }));

  const columns = [
    {
      title: "Сотрудник",
      key: "name",
      fixed: "left" as const,
      width: isMobile ? 140 : 220,
      render: (_: unknown, emp: Employee) => (
        <Space size={8} className="employee-cell">
          <EmployeeAvatar employee={emp} size={isMobile ? 28 : 32} />
          <span className="employee-cell-name">
            {emp.last_name} {emp.first_name}
            <br />
            <small style={{ color: "#888" }}>{emp.position}</small>
          </span>
        </Space>
      ),
    },
    ...skillColumns,
  ];

  return (
    <div>
      <Title level={3} style={{ marginBottom: 16 }}>
        Матрица компетенций
      </Title>
      <div className="legend-row">
        {[0, 1, 2, 3, 4, 5].map((l) => (
          <span key={l} className="legend-item">
            <span className="legend-swatch" style={{ background: LEVEL_COLORS[l] }} />
            <small>{l === 0 ? "не указан" : l === 5 ? "5 — эксперт" : l}</small>
          </span>
        ))}
      </div>
      <div className="page-table-wrap">
        <Table
          dataSource={employees}
          columns={columns}
          rowKey="id"
          scroll={{ x: "max-content" }}
          pagination={false}
          size="small"
          bordered
        />
      </div>
    </div>
  );
}
