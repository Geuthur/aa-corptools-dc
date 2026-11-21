// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA corptools_doctrine
import { apiClient } from "@/Api/Api";
import {
  createDoctrine,
  deleteDoctrine,
  loadManageDoctrines,
  manageQueryKeys,
  updateDoctrine,
} from "@/Api/calls/manage";

describe("manageQueryKeys", () => {
  it("provides the query keys", () => {
    expect(manageQueryKeys.doctrines).toEqual(["ManageDoctrines"]);
  });
});

describe("Manage API calls", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("loadManageDoctrines", () => {
    it("fetches manage doctrines list", async () => {
      // Test Data
      const mockList = [
        {
          id: 1,
          name: "Test Doctrine",
          category: "Cruiser",
          order_weight: 1,
          show_on_audit: true,
          skill_count: 5,
        },
      ];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockList,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadManageDoctrines();

      // Expected Result
      expect(result).toEqual(mockList);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/corptools_doctrine/api/manage/"
      );
    });
  });

  describe("updateDoctrine", () => {
    it("passes the doctrine id as path parameter", async () => {
      // Test Data
      const mockDoctrine = { id: 3, name: "Doctrine" };
      vi.spyOn(apiClient, "PUT").mockResolvedValueOnce({
        data: mockDoctrine,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await updateDoctrine(3, { name: "Doctrine" });

      // Expected Result
      expect(result).toEqual(mockDoctrine);
      expect(apiClient.PUT).toHaveBeenCalledWith(
        "/corptools_doctrine/api/manage/doctrine/{pk}/",
        {
          params: { path: { pk: 3 } },
          body: { name: "Doctrine" },
        }
      );
    });
  });
});

type Method = "GET" | "POST" | "PUT" | "DELETE";

/** Every call of `Api/calls/manage.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
  ["loadManageDoctrines", "GET", () => loadManageDoctrines(), "Failed to load doctrines for management"],
  [
    "createDoctrine",
    "POST",
    () => createDoctrine({ name: "Doctrine", category: null, order_weight: 1, skill_list: "Mining 1" }),
    "Failed to create doctrine",
  ],
  ["updateDoctrine", "PUT", () => updateDoctrine(3, { name: "Doctrine" }), "Failed to update doctrine 3"],
  ["deleteDoctrine", "DELETE", () => deleteDoctrine(3), "Failed to delete doctrine 3"],
];

const failWith = (method: Method, error: unknown) =>
  vi.spyOn(apiClient, method).mockResolvedValueOnce({
    data: undefined,
    error,
    response: new Response(),
  } as never);

describe("API call errors", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe.each(calls)("%s", (_name, method, call, fixedText) => {
    it("should throw the message of the API when the request fails", async () => {
      // Test Data
      failWith(method, { error: "Permission Denied" });

      // Test Action & Expected Result
      await expect(call()).rejects.toThrow("Permission Denied");
    });

    it("should throw the fixed text when the API sent no message", async () => {
      // Test Data
      failWith(method, {});

      // Test Action & Expected Result
      await expect(call()).rejects.toThrow(fixedText);
    });
  });
});
