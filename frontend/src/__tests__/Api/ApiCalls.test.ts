// Third Party
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA corptools_doctrine
import { apiClient } from "@/Api/Api";
import {
  loadDoctrines,
  loadManageDoctrines,
} from "@/Api/ApiCalls";

describe("General API client functions", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("loadDoctrines", () => {
    it("fetches doctrines for character", async () => {
      // Test Data
      const mockDoctrines = [
        {
          character: {
            character_id: 42,
            character_name: "Test",
            corporation_id: 1,
            corporation_name: "Corp",
          },
          doctrines: {},
        },
      ];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockDoctrines,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadDoctrines(42);

      // Expected Result
      expect(result).toEqual(mockDoctrines);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/corptools_doctrine/api/{character_id}/doctrines/",
        {
          params: { path: { character_id: 42 } },
        }
      );
    });

    it("fetches doctrines with targetCharacterId and allCharacters", async () => {
      // Test Data
      const mockDoctrines = [
        {
          character: {
            character_id: 42,
            character_name: "Test",
            corporation_id: 1,
            corporation_name: "Corp",
          },
          doctrines: {},
        },
      ];
      vi.spyOn(apiClient, "GET").mockResolvedValueOnce({
        data: mockDoctrines,
        error: undefined,
        response: new Response(),
      } as never);

      // Test Action
      const result = await loadDoctrines(42, 99, true);

      // Expected Result
      expect(result).toEqual(mockDoctrines);
      expect(apiClient.GET).toHaveBeenCalledWith(
        "/corptools_doctrine/api/{character_id}/doctrines/",
        {
          params: {
            path: { character_id: 42 },
            query: { target_character_id: 99, all_characters: true },
          },
        }
      );
    });
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
});
