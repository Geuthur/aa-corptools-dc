// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA corptools_doctrine
import { apiClient } from "@/Api/Api";
import type {
  CharacterDoctrines,
  DoctrineDetailResponse,
  MissingSkillsResponse,
} from "@/Api/schema";

/** Query keys of the doctrines area. */
export const doctrinesQueryKeys = {
  character: (characterId: number) => ["Doctrines", characterId] as const,
  missingSkills: (characterId: number, doctrineId: number) =>
    ["MissingSkills", characterId, doctrineId] as const,
  skills: (doctrineId: number, characterId?: number | null) =>
    ["DoctrineSkills", doctrineId, characterId ?? 0] as const,
};

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
    throw new Error(apiErrorMessage(error, `Failed to load doctrines for character ${characterId}`));
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
    throw new Error(apiErrorMessage(error, "Failed to load missing skills"));
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
    throw new Error(apiErrorMessage(error, "Failed to load doctrine skills"));
  }
  return data;
}
