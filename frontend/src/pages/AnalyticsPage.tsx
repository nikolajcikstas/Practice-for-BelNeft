import {
  Alert,
  Button,
  Card,
  Col,
  Empty,
  Grid,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
  message,
} from "antd";
import { useCallback, useEffect, useState } from "react";
import client from "../api/client";
import type { Report } from "../api/types";

const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

const REPORT_ORDER = [
  "top_skills",
  "booking_weekday",
  "booking_hours",
  "skill_levels",
  "skills_category",
  "top_employees",
];

const REPORT_HINTS: Record<string, string> = {
  top_skills:      "Какие навыки наиболее распространены в команде",
  booking_weekday: "В какие дни переговорная загружена сильнее всего",
  booking_hours:   "Пиковые часы использования переговорной",
  skill_levels:    "Насколько глубоко команда владеет навыками по категориям",
  skills_category: "Из каких категорий состоит арсенал знаний команды",
  top_employees:   "Кто из сотрудников обладает наибольшим набором компетенций",
};

export default function AnalyticsPage() {
  const screens = useBreakpoint();
  const isMobile = !screens.md;
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cacheKey, setCacheKey] = useState(Date.now());

  const load = useCallback(() => {
    setLoading(true);
    client
      .get<Report[]>("/reports")
      .then((r) => { setReports(r.data); setError(null); })
      .catch(() => setError("Не удалось загрузить отчёты"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleGenerate = async (fmt: "png" | "pdf") => {
    setGenerating(true);
    try {
      await client.post(`/reports/generate?fmt=${fmt}`);
      message.success(fmt === "pdf" ? "PDF-отчёты обновлены" : "Графики обновлены");
      setCacheKey(Date.now());
      load();
    } catch {
      message.error("Не удалось сгенерировать отчёты");
    } finally {
      setGenerating(false);
    }
  };

  const pngReports = REPORT_ORDER
    .map((id) => reports.find((r) => r.id === id && r.format === "png"))
    .filter(Boolean) as Report[];

  const pdfReports = reports.filter((r) => r.format === "pdf");

  const reportUrl = (filename: string) =>
    `/api/reports/files/${filename}?t=${cacheKey}`;

  if (loading) {
    return (
      <div className="page-loading">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <Title level={isMobile ? 4 : 3} style={{ margin: 0 }}>
          Аналитика и отчёты
        </Title>
        <Space wrap>
          <Button loading={generating} onClick={() => handleGenerate("png")}>
            Обновить графики
          </Button>
          <Button loading={generating} onClick={() => handleGenerate("pdf")}>
            Сгенерировать PDF
          </Button>
        </Space>
      </div>

      {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}

      <Space style={{ marginBottom: 16 }}>
        <Tag color="blue">Matplotlib</Tag>
        <Tag color="green">Seaborn</Tag>
        <Tag color="purple">Pandas + PostgreSQL</Tag>
        <Text type="secondary">{pngReports.length} графиков</Text>
      </Space>

      {pdfReports.length > 0 && (
        <Space wrap style={{ marginBottom: 16 }}>
          {pdfReports.map((r) => (
            <Button key={r.filename} size="small" href={reportUrl(r.filename)} target="_blank">
              {r.title} ↓ PDF
            </Button>
          ))}
        </Space>
      )}

      {pngReports.length === 0 ? (
        <Empty description="Отчёты ещё не сгенерированы">
          <Button type="primary" loading={generating} onClick={() => handleGenerate("png")}>
            Сгенерировать
          </Button>
        </Empty>
      ) : (
        <Row gutter={[16, 20]}>
          {pngReports.map((report) => (
            <Col key={report.id} xs={24} xl={12}>
              <Card
                title={report.title}
                extra={
                  <a href={reportUrl(report.filename)} target="_blank" rel="noreferrer">
                    Открыть
                  </a>
                }
              >
                {REPORT_HINTS[report.id] && (
                  <Text type="secondary" style={{ display: "block", marginBottom: 10, fontSize: 12 }}>
                    {REPORT_HINTS[report.id]}
                  </Text>
                )}
                <img
                  src={reportUrl(report.filename)}
                  alt={report.title}
                  style={{ width: "100%", height: "auto", display: "block" }}
                />
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}
