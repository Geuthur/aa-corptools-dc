// Third Party
import { type BaseColumnDef, renderTooltip } from "aa-geuthur-react";
import type { TFunction } from "i18next";
import { BookOpen, Edit2, Eye, EyeOff, Trash2 } from "lucide-react";
import { Badge, Button, ButtonGroup } from "react-bootstrap";

// AA corptools_doctrine
import type { ManageDoctrineSchema } from "@/Api/schema";

export const getManageDoctrinesColumns = (
  t: TFunction,
  isDeleting: boolean,
  onEdit: (doctrine: ManageDoctrineSchema) => void,
  onDelete: (doctrine: ManageDoctrineSchema) => void,
  onViewSkills: (doctrineId: number) => void
): BaseColumnDef<ManageDoctrineSchema>[] => [
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
      <ButtonGroup size="sm">
        {renderTooltip(
          t("View Skills"),
          <Button
            variant="info"
            aria-label={t("View Skills")}
            onClick={() => onViewSkills(row.original.id)}
          >
            <BookOpen size={14} />
          </Button>
        )}
        {renderTooltip(
          t("Edit Doctrine"),
          <Button
            variant="primary"
            aria-label={t("Edit Doctrine")}
            onClick={() => onEdit(row.original)}
          >
            <Edit2 size={14} />
          </Button>
        )}
        {renderTooltip(
          t("Delete Doctrine"),
          <Button
            variant="danger"
            aria-label={t("Delete Doctrine")}
            disabled={isDeleting}
            onClick={() => onDelete(row.original)}
          >
            <Trash2 size={14} />
          </Button>
        )}
      </ButtonGroup>
    ),
  },
];
