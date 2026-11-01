// React
import { MemoryRouter } from "react-router";

// Third Party
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

// AA corptools_doctrine
import BaseTable from "@/Components/Base/BaseTable/BaseTable";
import { createBaseColumnHelper } from "@/Components/Base/BaseTable/tableFeatures";

interface TestRow {
  id: number;
  name: string;
  role: string;
}

const columnHelper = createBaseColumnHelper<TestRow>();

const testColumns = [
  columnHelper.accessor("name", { header: "Name" }),
  columnHelper.accessor("role", { header: "Role" }),
];

const testData: TestRow[] = [
  { id: 1, name: "Alice", role: "Pilot" },
  { id: 2, name: "Bob", role: "Miner" },
  { id: 3, name: "Charlie", role: "Industrialist" },
];

const renderTable = (props?: Partial<React.ComponentProps<typeof BaseTable<TestRow>>>) =>
  render(
    <MemoryRouter>
      <BaseTable columns={testColumns} data={testData} {...props} />
    </MemoryRouter>,
  );

const firstColumnTexts = (container: HTMLElement) =>
  Array.from(container.querySelectorAll("tbody tr td:first-child")).map((cell) => cell.textContent);

describe("BaseTable", () => {
  it("test_render_should_display_all_rows", () => {
    // Test Action
    const { container } = renderTable({ variant: "bootstrap" });

    // Expected Result
    expect(firstColumnTexts(container)).toEqual(["Alice", "Bob", "Charlie"]);
  });

  it("test_render_should_display_rows_in_vowra_variant", () => {
    // Test Action
    renderTable();

    // Expected Result
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Charlie")).toBeInTheDocument();
  });

  it("test_initial_state_should_merge_partial_pagination", () => {
    // Test Action
    const { container } = renderTable({
      variant: "bootstrap",
      initialState: { pagination: { pageSize: 2 } },
    });

    // Expected Result: pageSize applies, pageIndex falls back to 0
    expect(firstColumnTexts(container)).toEqual(["Alice", "Bob"]);
    expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();
  });

  it("test_filter_should_hide_rows_not_matching_the_text_filter", async () => {
    // Test Data
    const user = userEvent.setup();
    const { container } = renderTable({ variant: "bootstrap" });
    const nameFilter = container.querySelectorAll("thead input")[0] as HTMLInputElement;

    // Test Action
    await user.type(nameFilter, "bo");

    // Expected Result: only Bob's row is left (checked on the cells)
    expect(firstColumnTexts(container)).toEqual(["Bob"]);
  });
});
