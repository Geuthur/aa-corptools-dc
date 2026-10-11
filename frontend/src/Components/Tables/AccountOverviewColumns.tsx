// React
import { Link } from "react-router";

// Third Party
import type { ColumnDef } from "@tanstack/react-table";
import type { TFunction } from "i18next";
import { ExternalLink } from "lucide-react";

// AA corptools_doctrine
import type { CharacterOverviewSchema } from "@/Api/schema";
import { ProjectName } from "@/configuration";

export const getAccountOverviewColumns = (
  t: TFunction
): ColumnDef<CharacterOverviewSchema>[] => [
  {
    id: "character",
    header: () => t("Character"),
    accessorKey: "character_name",
    cell: ({ row }) => (
      <div className="d-flex align-items-center gap-2">
        <img
          src={`https://images.evetech.net/characters/${row.original.character_id}/portrait?size=32`}
          alt={row.original.character_name}
          className="rounded-circle"
          width={30}
          height={30}
        />
        <span className="fw-semibold">{row.original.character_name}</span>
      </div>
    ),
  },
  {
    id: "corporation",
    header: () => t("Corporation"),
    accessorKey: "corporation_name",
    cell: ({ row }) => row.original.corporation_name,
  },
  {
    id: "alliance",
    header: () => t("Alliance"),
    accessorKey: "alliance_name",
    cell: ({ row }) => row.original.alliance_name || "-",
  },
  {
    id: "actions",
    header: () => t("Actions"),
    cell: ({ row }) => (
      <Link
        to={`/${ProjectName}/doctrine/${row.original.character_id}/`}
        className="aa-btn aa-btn-sm aa-btn-primary"
      >
        <ExternalLink size={14} />
        <span>{t("View Doctrines")}</span>
      </Link>
    ),
  },
];
