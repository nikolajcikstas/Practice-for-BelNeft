import {
  Alert,
  Button,
  Form,
  Grid,
  Input,
  Modal,
  Select,
  Spin,
  Table,
  Tag,
  Typography,
  message,
} from "antd";
import { useEffect, useState } from "react";
import client from "../api/client";
import type { Skill } from "../api/types";

const { Title } = Typography;
const { useBreakpoint } = Grid;

const CATEGORIES = [
  "Язык программирования",
  "СУБД",
  "Инструмент",
  "Фреймворк",
  "Другое",
];

export default function SkillsPage() {
  const screens = useBreakpoint();
  const isMobile = !screens.md;
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = () => {
    setLoading(true);
    client
      .get<Skill[]>("/skills")
      .then((r) => { setSkills(r.data); setError(null); })
      .catch(() => setError("Не удалось загрузить навыки"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    const values = await form.validateFields();
    try {
      await client.post("/skills", values);
      message.success("Навык добавлен");
      setModalOpen(false);
      form.resetFields();
      load();
    } catch (err: unknown) {
      const e = err as { response?: { status?: number; data?: { detail?: string } } };
      if (e.response?.status === 409) {
        message.error(e.response.data?.detail ?? "Навык уже существует");
      } else {
        message.error("Ошибка при создании навыка");
      }
    }
  };

  const handleDelete = (skill: Skill) => {
    Modal.confirm({
      title: `Удалить навык «${skill.name}»?`,
      content: "Связи с сотрудниками будут удалены автоматически.",
      okType: "danger",
      onOk: async () => {
        try {
          await client.delete(`/skills/${skill.id}`);
          message.success("Навык удалён");
          load();
        } catch {
          message.error("Ошибка при удалении");
        }
      },
    });
  };

  const columns = [
    {
      title: "Название",
      dataIndex: "name",
      sorter: (a: Skill, b: Skill) => a.name.localeCompare(b.name),
    },
    {
      title: "Категория",
      dataIndex: "category",
      render: (cat: string) => <Tag color="blue">{cat}</Tag>,
      filters: [...new Set(skills.map((s) => s.category))].map((c) => ({
        text: c,
        value: c,
      })),
      onFilter: (value: unknown, record: Skill) => record.category === value,
    },
    {
      title: "Действие",
      width: isMobile ? 90 : undefined,
      render: (_: unknown, skill: Skill) => (
        <Button size="small" danger onClick={() => handleDelete(skill)}>
          Удалить
        </Button>
      ),
    },
  ];

  if (loading) return <Spin size="large" className="page-spinner" />;
  if (error) return <Alert type="error" message={error} />;

  return (
    <div>
      <div className="page-header">
        <Title level={3}>Справочник навыков</Title>
        <Button type="primary" onClick={() => { form.resetFields(); setModalOpen(true); }}>
          + Добавить
        </Button>
      </div>

      <div className="page-table-wrap">
        <Table
          dataSource={skills}
          columns={columns}
          rowKey="id"
          bordered
          size={isMobile ? "small" : "middle"}
          scroll={{ x: isMobile ? 480 : undefined }}
          pagination={{ pageSize: 20 }}
        />
      </div>

      <Modal
        title="Новый навык"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={handleCreate}
        okText="Добавить"
        width={isMobile ? "100%" : 520}
        style={isMobile ? { top: 20, maxWidth: "calc(100vw - 16px)" } : undefined}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="Название навыка"
            rules={[{ required: true, message: "Введите название" }]}
          >
            <Input placeholder="Например: Python" />
          </Form.Item>
          <Form.Item
            name="category"
            label="Категория"
            rules={[{ required: true, message: "Выберите категорию" }]}
          >
            <Select
              showSearch
              placeholder="Выберите категорию"
              options={CATEGORIES.map((c) => ({ value: c, label: c }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
