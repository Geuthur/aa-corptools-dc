// React
import React, { useState } from "react";

// Third Party
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { PlusCircle, Save, X } from "lucide-react";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA corptools_doctrine
import { createDoctrine, updateDoctrine } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import type { ManageDoctrineSchema } from "@/Api/schema";

interface ManageDoctrineModalProps {
  show: boolean;
  onHide: () => void;
  doctrineToEdit?: ManageDoctrineSchema | null;
}

const ManageDoctrineForm: React.FC<{
  onHide: () => void;
  doctrineToEdit?: ManageDoctrineSchema | null;
}> = ({ onHide, doctrineToEdit }) => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const isEditing = Boolean(doctrineToEdit);

  const [name, setName] = useState(doctrineToEdit?.name ?? "");
  const [category, setCategory] = useState(doctrineToEdit?.category ?? "");
  const [orderWeight, setOrderWeight] = useState(doctrineToEdit?.order_weight ?? 0);
  const [showOnAudit, setShowOnAudit] = useState(doctrineToEdit?.show_on_audit ?? true);
  const [skillList, setSkillList] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      if (isEditing && doctrineToEdit) {
        return updateDoctrine(doctrineToEdit.id, {
          name,
          category: category || null,
          order_weight: Number(orderWeight),
          show_on_audit: showOnAudit,
        });
      }
      return createDoctrine({
        name,
        category: category || null,
        order_weight: Number(orderWeight),
        skill_list: skillList,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.ManageDoctrines });
      onHide();
    },
    onError: (err: unknown) => {
      setErrorMessage(
        err instanceof Error
          ? err.message
          : t("An error occurred while saving the doctrine.")
      );
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!name.trim()) {
      setErrorMessage(t("Please enter a doctrine name."));
      return;
    }

    if (!isEditing && !skillList.trim()) {
      setErrorMessage(t("Please provide a skill plan."));
      return;
    }

    mutation.mutate();
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Modal.Header closeButton>
        <Modal.Title className="d-flex align-items-center gap-2">
          {isEditing ? <Save size={20} /> : <PlusCircle size={20} />}
          {isEditing ? t("Edit Doctrine") : t("Add New Doctrine")}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {errorMessage && (
          <Alert variant="danger" dismissible onClose={() => setErrorMessage(null)}>
            {errorMessage}
          </Alert>
        )}

        <Form.Group className="mb-3" controlId="doctrineName">
          <Form.Label>{t("Doctrine Name")}</Form.Label>
          <Form.Control
            type="text"
            placeholder={t("e.g. Cerberus Fleet")}
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="doctrineCategory">
          <Form.Label>{t("Category")}</Form.Label>
          <Form.Control
            type="text"
            placeholder={t("e.g. Cruiser, Battleship, Logistics, etc.")}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
        </Form.Group>

        <Form.Group className="mb-3" controlId="doctrineOrderWeight">
          <Form.Label>{t("Order Weight (0 - 999)")}</Form.Label>
          <Form.Control
            type="number"
            min={0}
            max={999}
            value={orderWeight}
            onChange={(e) => setOrderWeight(parseInt(e.target.value, 10) || 0)}
          />
          <Form.Text className="text-muted">
            {t("Lower numbers appear first in lists.")}
          </Form.Text>
        </Form.Group>

        {isEditing && (
          <Form.Group className="mb-3" controlId="doctrineShowOnAudit">
            <Form.Check
              type="switch"
              id="show-on-audit-switch"
              label={t("Show on Character Audit")}
              checked={showOnAudit}
              onChange={(e) => setShowOnAudit(e.target.checked)}
            />
          </Form.Group>
        )}

        {!isEditing && (
          <Form.Group className="mb-3" controlId="doctrineSkillList">
            <Form.Label>{t("Skill List (Skill Plan / EFT format)")}</Form.Label>
            <Form.Control
              as="textarea"
              rows={8}
              placeholder={t(
                "Paste your skill plan here. Format: One skill per line (e.g. Minmatar Cruiser 4 or <localized ...>)\nMinmatar Cruiser 4\nHeavy Missile Specialization 3"
              )}
              value={skillList}
              onChange={(e) => setSkillList(e.target.value)}
              required
            />
          </Form.Group>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button
          variant="primary"
          type="submit"
          disabled={mutation.isPending}
          className="d-flex align-items-center gap-1"
        >
          {mutation.isPending ? (
            <span className="spinner-border spinner-border-sm" role="status" />
          ) : isEditing ? (
            <Save size={16} />
          ) : (
            <PlusCircle size={16} />
          )}
          {mutation.isPending
            ? t("Saving...")
            : isEditing
            ? t("Save Changes")
            : t("Create Doctrine")}
        </Button>
        <Button
          variant="secondary"
          onClick={onHide}
          disabled={mutation.isPending}
          className="d-flex align-items-center gap-1"
        >
          <X size={16} />
          {t("Cancel")}
        </Button>
      </Modal.Footer>
    </Form>
  );
};

export const ManageDoctrineModal: React.FC<ManageDoctrineModalProps> = ({
  show,
  onHide,
  doctrineToEdit,
}) => {
  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      {show && (
        <ManageDoctrineForm
          key={doctrineToEdit?.id ?? "new"}
          onHide={onHide}
          doctrineToEdit={doctrineToEdit}
        />
      )}
    </Modal>
  );
};

export default ManageDoctrineModal;
