// Third Party
import type { ColumnDef } from "@tanstack/react-table";
import type { TFunction } from "i18next";
import { BookOpen, Edit2, Eye, EyeOff, Trash2 } from "lucide-react";
import { Badge, Button } from "react-bootstrap";

// AA corptools_doctrine
import type { ManageDoctrineSchema } from "@/Api/schema";

export const getManageDoctrinesColumns = (
  t: TFunction,
  isDeleting: boolean,
  onEdit: (doctrine: ManageDoctrineSchema) => void,
  onDelete: (doctrine: ManageDoctrineSchema) => void,
  onViewSkills: (doctrineId: number) => void
): ColumnDef<ManageDoctrineSchema>[] => [
  {
    id: "name",
    header: () => t("Doctrine Name"),
    accessorKey: "name",
    cell: ({ row }) => (
      <div className="d-flex align-items-center gap-2">
        <span className="fw-bold">{row.original.name}</span>
        <Badge bg="secondary" pill title={t("Required Skills Count")}>
          {row.original.skill_count} {t("skills")}
        </Badge>
      </div>
    ),
  },
  {
    id: "category",
    header: () => t("Category"),
    accessorKey: "category",
    cell: ({ row }) => (
      <Badge bg="info">{row.original.category || t("Uncategorized")}</Badge>
    ),
  },
  {
    id: "order_weight",
    header: () => t("Order Weight"),
    accessorKey: "order_weight",
    cell: ({ row }) => (
      <span className="text-muted">{row.original.order_weight}</span>
    ),
  },
  {
    id: "show_on_audit",
    header: () => t("Show on Audit"),
    accessorKey: "show_on_audit",
    cell: ({ row }) =>
      row.original.show_on_audit ? (
        <Badge bg="success" className="d-flex align-items-center gap-1 w-fit">
          <Eye size={12} />
          <span>{t("Active")}</span>
        </Badge>
      ) : (
        <Badge bg="secondary" className="d-flex align-items-center gap-1 w-fit">
          <EyeOff size={12} />
          <span>{t("Hidden")}</span>
        </Badge>
      ),
  },
  {
    id: "actions",
    header: () => t("Actions"),
    cell: ({ row }) => (
      <div className="d-flex align-items-center gap-2">
        <Button
          size="sm"
          variant="outline-info"
          title={t("View Skills")}
          onClick={() => onViewSkills(row.original.id)}
          className="d-flex align-items-center gap-1"
        >
          <BookOpen size={14} />
          <span>{t("Skills")}</span>
        </Button>

        <Button
          size="sm"
          variant="outline-primary"
          title={t("Edit Doctrine")}
          onClick={() => onEdit(row.original)}
          className="d-flex align-items-center gap-1"
        >
          <Edit2 size={14} />
          <span>{t("Edit")}</span>
        </Button>

        <Button
          size="sm"
          variant="outline-danger"
          title={t("Delete Doctrine")}
          disabled={isDeleting}
          onClick={() => onDelete(row.original)}
          className="d-flex align-items-center gap-1"
        >
          <Trash2 size={14} />
          <span>{t("Delete")}</span>
        </Button>
      </div>
    ),
  },
];
