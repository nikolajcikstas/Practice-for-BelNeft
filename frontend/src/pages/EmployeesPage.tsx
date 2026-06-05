import {
  Alert,
  Button,
  Drawer,
  Form,
  Input,
  Modal,
  Select,
  Slider,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import { useEffect, useState } from "react";
import client from "../api/client";
import type { Employee, Skill } from "../api/types";
import EmployeeAvatar from "../components/EmployeeAvatar";

const { Title } = Typography;

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Employee | null>(null);
  const [skillModalOpen, setSkillModalOpen] = useState(false);
  const [skillTarget, setSkillTarget] = useState<Employee | null>(null);
  const [form] = Form.useForm();
  const [skillForm] = Form.useForm();

  const load = () => {
    setLoading(true);
    Promise.all([
      client.get<{ items: Employee[] }>("/employees?size=100"),
      client.get<Skill[]>("/skills"),
    ])
      .then(([e, s]) => {
        setEmployees(e.data.items);
        setSkills(s.data);
      })
      .catch(() => setError("Не удалось загрузить данные"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditTarget(null);
    form.resetFields();
    setDrawerOpen(true);
  };

  const openEdit = (emp: Employee) => {
    setEditTarget(emp);
    form.setFieldsValue(emp);
    setDrawerOpen(true);
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    if (editTarget) {
      await client.patch(`/employees/${editTarget.id}`, values);
      message.success("Сотрудник обновлён");
    } else {
      await client.post("/employees", values);
      message.success("Сотрудник добавлен");
    }
    setDrawerOpen(false);
    load();
  };

  const handleDelete = (emp: Employee) => {
    Modal.confirm({
      title: `Удалить сотрудника ${emp.last_name} ${emp.first_name}?`,
      okType: "danger",
      onOk: async () => {
        await client.delete(`/employees/${emp.id}`);
        message.success("Удалено");
        load();
      },
    });
  };

  const openSkillModal = (emp: Employee) => {
    setSkillTarget(emp);
    skillForm.resetFields();
    setSkillModalOpen(true);
  };

  const handleAssignSkill = async () => {
    const values = await skillForm.validateFields();
    await client.post(`/employees/${skillTarget!.id}/skills`, values);
    message.success("Навык назначен");
    setSkillModalOpen(false);
    load();
  };

  const columns = [
    {
      title: "Сотрудник",
      render: (_: unknown, emp: Employee) => (
        <Space>
          <EmployeeAvatar employee={emp} size={40} />
          <span>
            {emp.last_name} {emp.first_name}
          </span>
        </Space>
      ),
    },
    { title: "Должность", dataIndex: "position" },
    {
      title: "Навыки",
      render: (_: unknown, emp: Employee) =>
        emp.skills.map((s) => (
          <Tag key={s.skill_id} color="blue">
            {s.name}: {s.proficiency_level}
          </Tag>
        )),
    },
    {
      title: "Действия",
      render: (_: unknown, emp: Employee) => (
        <Space>
          <Button size="small" onClick={() => openEdit(emp)}>Редактировать</Button>
          <Button size="small" onClick={() => openSkillModal(emp)}>+ Навык</Button>
          <Button size="small" danger onClick={() => handleDelete(emp)}>Удалить</Button>
        </Space>
      ),
    },
  ];

  if (loading) return <Spin size="large" style={{ marginTop: 80, display: "block", textAlign: "center" }} />;
  if (error) return <Alert type="error" message={error} />;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>Сотрудники</Title>
        <Button type="primary" onClick={openCreate}>+ Добавить</Button>
      </div>

      <Table dataSource={employees} columns={columns} rowKey="id" bordered size="middle" />

      <Drawer
        title={editTarget ? "Редактировать сотрудника" : "Новый сотрудник"}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={420}
        extra={<Button type="primary" onClick={handleSave}>Сохранить</Button>}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="last_name" label="Фамилия" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="first_name" label="Имя" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="position" label="Должность" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="photo_url" label="URL фото">
            <Input placeholder="https://..." />
          </Form.Item>
        </Form>
      </Drawer>

      <Modal
        title={`Назначить навык — ${skillTarget?.last_name} ${skillTarget?.first_name}`}
        open={skillModalOpen}
        onCancel={() => setSkillModalOpen(false)}
        onOk={handleAssignSkill}
        okText="Назначить"
      >
        <Form form={skillForm} layout="vertical">
          <Form.Item name="skill_id" label="Навык" rules={[{ required: true }]}>
            <Select
              showSearch
              optionFilterProp="label"
              options={skills.map((s) => ({
                value: s.id,
                label: `${s.name} (${s.category})`,
              }))}
            />
          </Form.Item>
          <Form.Item name="proficiency_level" label="Уровень владения (0–5)" initialValue={1}>
            <Slider min={0} max={5} marks={{ 0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5" }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
