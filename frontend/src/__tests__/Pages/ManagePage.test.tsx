// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA corptools_doctrine
import * as ApiCalls from "@/Api/ApiCalls";
import ManagePage from "@/Pages/ManagePage";

vi.mock("@/Api/ApiCalls", () => ({
  loadManageDoctrines: vi.fn(),
  deleteDoctrine: vi.fn(),
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
  withTranslation: () => (Component: unknown) => Component,
}));

const renderPage = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/corptools_doctrine/manage/"]}>
        <ManagePage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe("ManagePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render manage doctrines table and add button", async () => {
    // Test Data
    vi.mocked(ApiCalls.loadManageDoctrines).mockResolvedValue([
      {
        id: 1,
        name: "Cerberus Fleet",
        category: "Cruiser",
        order_weight: 1,
        show_on_audit: true,
        skill_count: 5,
      },
    ]);

    // Test Action
    renderPage();

    // Expected Result
    expect(await screen.findByText("Cerberus Fleet")).toBeTruthy();
    expect(screen.getByText("Cruiser")).toBeTruthy();
    expect(screen.getByText("Add Doctrine")).toBeTruthy();
    expect(screen.getByText("5 skills")).toBeTruthy();
  });

  it("should render the row actions as icon buttons in a button group", async () => {
    // Test Data
    vi.mocked(ApiCalls.loadManageDoctrines).mockResolvedValue([
      {
        id: 1,
        name: "Cerberus Fleet",
        category: "Cruiser",
        order_weight: 1,
        show_on_audit: true,
        skill_count: 5,
      },
    ]);

    // Test Action
    renderPage();

    // Expected Result
    await screen.findByText("Cerberus Fleet");
    const view = screen.getByLabelText("View Skills");
    const edit = screen.getByLabelText("Edit Doctrine");
    const remove = screen.getByLabelText("Delete Doctrine");
    expect(view.parentElement?.classList.contains("btn-group-sm")).toBe(true);
    expect(edit.parentElement).toBe(view.parentElement);
    expect(remove.parentElement).toBe(view.parentElement);
  });
});
