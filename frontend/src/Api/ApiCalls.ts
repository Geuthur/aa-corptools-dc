// AA corptools_doctrine
import { apiClient } from "@/Api/Api";
import type {
  CharacterDoctrines,
  CharacterOverviewSchema,
  CorporationDoctrines,
  CorporationMembersResponse,
  CorporationOverviewSchema,
  DoctrineCreateRequest,
  DoctrineDetailResponse,
  DoctrineUpdateRequest,
  ManageDoctrineSchema,
  MenuSchema,
  MissingSkillsResponse,
  UserData,
} from "@/Api/schema";

export async function loadUserData(): Promise<{ user: UserData }> {
  const { data, error } = await apiClient.GET("/corptools_doctrine/api/user/");
  if (error || !data) {
    throw new Error("Failed to load user data");
  }
  return { user: data };
}

export async function loadMenu(): Promise<MenuSchema> {
  const { data, error } = await apiClient.GET("/corptools_doctrine/api/menu/");
  if (error || !data) {
    throw new Error("Failed to load menu");
  }
  return data;
}

export async function loadDoctrines(
  characterId: number,
  targetCharacterId?: number | null,
  allCharacters?: boolean
): Promise<CharacterDoctrines[]> {
  const queryParams: {
    target_character_id?: number | null;
    all_characters?: boolean;
  } = {};
  if (targetCharacterId !== undefined) {
    queryParams.target_character_id = targetCharacterId;
  }
  if (allCharacters !== undefined) {
    queryParams.all_characters = allCharacters;
  }

  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/{character_id}/doctrines/",
    {
      params: {
        path: { character_id: characterId },
        query: Object.keys(queryParams).length > 0 ? queryParams : undefined,
      },
    }
  );
  if (error || !data) {
    throw new Error(`Failed to load doctrines for character ${characterId}`);
  }
  return data;
}

export async function loadCorporationDoctrines(
  corporationId: number,
  category?: string,
  doctrineIds?: number[]
): Promise<CorporationDoctrines[]> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/{corporation_id}/doctrines/view/corporation/",
    {
      params: {
        path: { corporation_id: corporationId },
        query: {
          category: category,
          doctrine_ids: doctrineIds,
        },
      },
    }
  );
  if (error || !data) {
    throw new Error(
      `Failed to load corporation doctrines for corporation ${corporationId}`
    );
  }
  return data;
}

export async function loadCorporationMembers(
  corporationId: number
): Promise<CorporationMembersResponse> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/{corporation_id}/doctrines/members/",
    {
      params: {
        path: { corporation_id: corporationId },
      },
    }
  );
  if (error || !data) {
    throw new Error(
      `Failed to load members for corporation ${corporationId}`
    );
  }
  return data;
}

export async function auditCorporationMembers(
  corporationId: number,
  characterIds?: number[],
  category?: string,
  doctrineIds?: number[]
): Promise<CorporationDoctrines[]> {
  const { data, error } = await apiClient.POST(
    "/corptools_doctrine/api/{corporation_id}/doctrines/audit-members/",
    {
      params: {
        path: { corporation_id: corporationId },
      },
      body: {
        character_ids: characterIds,
        category: category,
        doctrine_ids: doctrineIds,
      },
    }
  );
  if (error || !data) {
    throw new Error(
      `Failed to audit members for corporation ${corporationId}`
    );
  }
  return data;
}

export async function loadAccountOverview(): Promise<CharacterOverviewSchema[]> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/account/overview/"
  );
  if (error || !data) {
    throw new Error("Failed to load account overview");
  }
  return data;
}

export async function loadCorporationOverview(): Promise<
  CorporationOverviewSchema[]
> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/corporation/overview/"
  );
  if (error || !data) {
    throw new Error("Failed to load corporation overview");
  }
  return data;
}

export async function loadMissingSkills(
  characterId: number,
  doctrineId: number
): Promise<MissingSkillsResponse> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/{character_id}/doctrines/{pk}/",
    {
      params: {
        path: { character_id: characterId, pk: doctrineId },
      },
    }
  );
  if (error || !data) {
    throw new Error("Failed to load missing skills");
  }
  return data;
}

export async function loadDoctrineSkills(
  doctrineId: number,
  characterId?: number | null
): Promise<DoctrineDetailResponse> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/doctrines/{pk}/",
    {
      params: {
        path: { pk: doctrineId },
        query: characterId ? { character_id: characterId } : undefined,
      },
    }
  );
  if (error || !data) {
    throw new Error("Failed to load doctrine skills");
  }
  return data;
}

export async function loadManageDoctrines(): Promise<ManageDoctrineSchema[]> {
  const { data, error } = await apiClient.GET(
    "/corptools_doctrine/api/manage/"
  );
  if (error || !data) {
    throw new Error("Failed to load doctrines for management");
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
    throw new Error("Failed to create doctrine");
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
    throw new Error(`Failed to update doctrine ${pk}`);
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
    throw new Error(`Failed to delete doctrine ${pk}`);
  }
  return data as { success: boolean; message: string };
}
