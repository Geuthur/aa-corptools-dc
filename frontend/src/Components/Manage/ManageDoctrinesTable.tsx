// React
import React, { useMemo } from "react";

// Third Party
import { useTranslation } from "react-i18next";

// AA corptools_doctrine
import type { ManageDoctrineSchema } from "@/Api/schema";
import BaseTable from "@/Components/Base/BaseTable";
import { getManageDoctrinesColumns } from "@/Components/Tables";

export interface ManageDoctrinesTableProps {
  data: ManageDoctrineSchema[];
  isLoading: boolean;
  isError: boolean;
  isDeleting: boolean;
  onEdit: (doctrine: ManageDoctrineSchema) => void;
  onDelete: (doctrine: ManageDoctrineSchema) => void;
  onViewSkills: (doctrineId: number) => void;
}

export const ManageDoctrinesTable: React.FC<ManageDoctrinesTableProps> = ({
  data,
  isLoading,
  isError,
  isDeleting,
  onEdit,
  onDelete,
  onViewSkills,
}) => {
  const { t } = useTranslation();

  const columns = useMemo(
    () =>
      getManageDoctrinesColumns(
        t,
        isDeleting,
        onEdit,
        onDelete,
        onViewSkills
      ),
    [t, isDeleting, onEdit, onDelete, onViewSkills]
  );

  return (
    <BaseTable
      columns={columns}
      data={data}
      isFetching={isLoading}
      isError={isError}
      striped
      hover
    />
  );
};

export default ManageDoctrinesTable;
