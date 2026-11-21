// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA corptools_doctrine
import { apiClient } from "@/Api/Api";
import type {
  DoctrineCreateRequest,
  DoctrineUpdateRequest,
  ManageDoctrineSchema,
} from "@/Api/schema";

/** Query keys of the manage area. */
export const manageQueryKeys = {
  doctrines: ["ManageDoctrines"] as const,
};

export async function loadManageDoctrines(): Promise<ManageDoctrineSchema[]> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/manage/"
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load doctrines for management"));
  }
  return data;
}

export async function createDoctrine(
  payload: DoctrineCreateRequest
): Promise<ManageDoctrineSchema> {
  const { data, error } = await apiClient.POST(
    "/corptools_doctrine/api/manage/doctrine/",
    {
      body: payload,
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to create doctrine"));
  }
  return data;
}

export async function updateDoctrine(
  pk: number,
  payload: DoctrineUpdateRequest
): Promise<ManageDoctrineSchema> {
  const { data, error } = await apiClient.PUT(
    "/corptools_doctrine/api/manage/doctrine/{pk}/",
    {
      params: {
        path: { pk },
      },
      body: payload,
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, `Failed to update doctrine ${pk}`));
  }
  return data;
}

export async function deleteDoctrine(
  pk: number
): Promise<{ success: boolean; message: string }> {
  const { data, error } = await apiClient.DELETE(
    "/corptools_doctrine/api/manage/doctrine/{pk}/",
    {
      params: {
        path: { pk },
      },
    }
  );
  if (error || !data) {
    throw new Error(apiErrorMessage(error, `Failed to delete doctrine ${pk}`));
  }
  return data as { success: boolean; message: string };
}
