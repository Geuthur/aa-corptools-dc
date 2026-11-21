// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA corptools_doctrine
import { apiClient } from "@/Api/Api";
import type {
  CharacterOverviewSchema,
} from "@/Api/schema";

/** Query keys of the account area. */
export const accountQueryKeys = {
  overview: ["AccountOverview"] as const,
};

export async function loadAccountOverview(): Promise<CharacterOverviewSchema[]> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/account/overview/"
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load account overview"));
  }
  return data;
}
