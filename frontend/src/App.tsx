import { MenuOutlined } from "@ant-design/icons";
import { Button, Drawer, Grid, Layout, Menu } from "antd";
import { useState } from "react";
import BookingPage from "./pages/BookingPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import EmployeesPage from "./pages/EmployeesPage";
import SkillsMatrixPage from "./pages/SkillsMatrixPage";
import SkillsPage from "./pages/SkillsPage";

const { Header, Content, Sider } = Layout;
const { useBreakpoint } = Grid;

type Page = "matrix" | "employees" | "skills" | "booking" | "analytics";

const MENU_ITEMS = [
  { key: "matrix", label: "Матрица компетенций" },
  { key: "employees", label: "Сотрудники" },
  { key: "skills", label: "Справочник навыков" },
  { key: "booking", label: "Переговорная" },
  { key: "analytics", label: "Аналитика" },
];

export default function App() {
  const [page, setPage] = useState<Page>("matrix");
  const [navOpen, setNavOpen] = useState(false);
  const screens = useBreakpoint();
  const isMobile = !screens.md;

  const goTo = (key: string) => {
    setPage(key as Page);
    setNavOpen(false);
  };

  const menu = (
    <Menu
      mode="inline"
      selectedKeys={[page]}
      items={MENU_ITEMS}
      onClick={(e) => goTo(e.key)}
    />
  );

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        {isMobile && (
          <Button
            type="text"
            icon={<MenuOutlined />}
            className="app-menu-btn"
            onClick={() => setNavOpen(true)}
          />
        )}
        <span className="app-title">Портал компетенций</span>
      </Header>

      <Layout>
        {!isMobile && (
          <Sider width={220} className="app-sider">
            {menu}
          </Sider>
        )}

        {isMobile && (
          <Drawer
            title="Меню"
            placement="left"
            open={navOpen}
            onClose={() => setNavOpen(false)}
            width={280}
            className="app-nav-drawer"
          >
            {menu}
          </Drawer>
        )}

        <Content className="app-content">
          {page === "matrix" && <SkillsMatrixPage />}
          {page === "employees" && <EmployeesPage />}
          {page === "skills" && <SkillsPage />}
          {page === "booking" && <BookingPage />}
          {page === "analytics" && <AnalyticsPage />}
        </Content>
      </Layout>
    </Layout>
  );
}
