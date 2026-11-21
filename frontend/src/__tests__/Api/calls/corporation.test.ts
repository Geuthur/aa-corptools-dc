// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA corptools_doctrine
import { apiClient } from "@/Api/Api";
import {
  auditCorporationMembers,
  corporationQueryKeys,
  loadCorporationDoctrines,
  loadCorporationMembers,
  loadCorporationOverview,
} from "@/Api/calls/corporation";

describe("corporationQueryKeys", () => {
  it("provides the query keys", () => {
    expect(corporationQueryKeys.doctrines(7)).toEqual(["CorporationDoctrines", 7]);
    expect(corporationQueryKeys.members(7)).toEqual(["CorporationMembers", 7]);
    expect(corporationQueryKeys.overview).toEqual(["CorporationOverview"]);
  });
});

describe("Corporation API calls", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("loadCorporationMembers", () => {
    it("passes the corporation id as path parameter", async () => {
      // Test Data
      const mockMembers = { corporation_id: 7, members: [] };
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockMembers,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadCorporationMembers(7);

      // Expected Result
      expect(result).toEqual(mockMembers);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/corptools_doctrine/api/{corporation_id}/doctrines/members/",
        {
          params: { path: { corporation_id: 7 } },
        }
      );
    });
  });
});

type Method = "GET" | "POST" | "PUT" | "DELETE";

/** Every call of `Api/calls/corporation.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
  [
    "loadCorporationDoctrines",
    "GET",
    () => loadCorporationDoctrines(7),
    "Failed to load corporation doctrines for corporation 7",
  ],
  ["loadCorporationMembers", "GET", () => loadCorporationMembers(7), "Failed to load members for corporation 7"],
  ["auditCorporationMembers", "POST", () => auditCorporationMembers(7), "Failed to audit members for corporation 7"],
  ["loadCorporationOverview", "GET", () => loadCorporationOverview(), "Failed to load corporation overview"],
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
