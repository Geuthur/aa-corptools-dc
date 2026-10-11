// React
import React, { useMemo } from "react";

// Third Party
import { useTranslation } from "react-i18next";

// AA corptools_doctrine
import type { CorporationOverviewSchema } from "@/Api/schema";
import BaseTable from "@/Components/Base/BaseTable";
import { getCorporationOverviewColumns } from "@/Components/Tables";

export interface CorporationOverviewTableProps {
  data: CorporationOverviewSchema[];
  isLoading: boolean;
  isError: boolean;
}

export const CorporationOverviewTable: React.FC<CorporationOverviewTableProps> = ({
  data,
  isLoading,
  isError,
}) => {
  const { t } = useTranslation();

  const columns = useMemo(
    () => getCorporationOverviewColumns(t),
    [t]
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

export default CorporationOverviewTable;
