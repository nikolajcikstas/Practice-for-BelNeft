import { Layout, Menu } from "antd";
import { useState } from "react";
import BookingPage from "./pages/BookingPage";
import EmployeesPage from "./pages/EmployeesPage";
import SkillsMatrixPage from "./pages/SkillsMatrixPage";

const { Header, Content, Sider } = Layout;

type Page = "employees" | "matrix" | "booking";

export default function App() {
  const [page, setPage] = useState<Page>("matrix");

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ color: "#fff", fontWeight: 700, fontSize: 18 }}>
          Портал компетенций
        </span>
      </Header>
      <Layout>
        <Sider width={220} style={{ background: "#fff" }}>
          <Menu
            mode="inline"
            selectedKeys={[page]}
            style={{ height: "100%", borderRight: 0 }}
            onClick={(e) => setPage(e.key as Page)}
            items={[
              { key: "matrix", label: "Матрица компетенций" },
              { key: "employees", label: "Сотрудники" },
              { key: "booking", label: "Переговорная" },
            ]}
          />
        </Sider>
        <Content style={{ padding: 24 }}>
          {page === "matrix" && <SkillsMatrixPage />}
          {page === "employees" && <EmployeesPage />}
          {page === "booking" && <BookingPage />}
        </Content>
      </Layout>
    </Layout>
  );
}
