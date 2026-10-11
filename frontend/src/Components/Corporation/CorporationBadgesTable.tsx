// React
import React, { useMemo } from "react";

// Third Party
import { useTranslation } from "react-i18next";

// AA corptools_doctrine
import type { ActiveDoctrineOverview } from "@/Api/schema";
import BaseTable from "@/Components/Base/BaseTable";
import type { MemberDoctrineRow } from "@/Components/Corporation/types";
import { getCorporationBadgesColumns } from "@/Components/Tables";

export interface CorporationBadgesTableProps {
  members: MemberDoctrineRow[];
  activeDoctrines: ActiveDoctrineOverview[];
  onOpenSkills: (doctrineId: number, characterId?: number) => void;
  onOpenMissingSkills: (charId: number, doctrineId: number) => void;
}

export const CorporationBadgesTable: React.FC<CorporationBadgesTableProps> = ({
  members,
  activeDoctrines,
  onOpenSkills,
  onOpenMissingSkills,
}) => {
  const { t } = useTranslation();

  const columns = useMemo(
    () =>
      getCorporationBadgesColumns(
        t,
        activeDoctrines,
        onOpenSkills,
        onOpenMissingSkills
      ),
    [activeDoctrines, t, onOpenSkills, onOpenMissingSkills]
  );

  return (
    <BaseTable
      columns={columns}
      data={members}
      striped
      hover
      itemLabel={t("members")}
    />
  );
};

export default CorporationBadgesTable;
