// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA corptools_doctrine
import { apiClient } from "@/Api/Api";
import {
  accountQueryKeys,
  loadAccountOverview,
} from "@/Api/calls/account";

describe("accountQueryKeys", () => {
  it("provides the query keys", () => {
    expect(accountQueryKeys.overview).toEqual(["AccountOverview"]);
  });
});

describe("Account API calls", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("loadAccountOverview", () => {
    it("fetches the account overview", async () => {
      // Test Data
      const mockOverview = [{ character_id: 42 }];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockOverview,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadAccountOverview();

      // Expected Result
      expect(result).toEqual(mockOverview);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/corptools_doctrine/api/account/overview/"
      );
    });
  });
});

type Method = "GET" | "POST" | "PUT" | "DELETE";

/** Every call of `Api/calls/account.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
  ["loadAccountOverview", "GET", () => loadAccountOverview(), "Failed to load account overview"],
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
