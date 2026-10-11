// React
import React, { useCallback, useState } from "react";

// Third Party
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA corptools_doctrine
import { deleteDoctrine, loadManageDoctrines } from "@/Api/ApiCalls";
import { queryKeys } from "@/Api/query";
import type { ManageDoctrineSchema } from "@/Api/schema";
import { ManageDoctrinesTable, ManageHeader } from "@/Components/Manage";
import DoctrineSkillsModal from "@/Components/Modals/DoctrineSkillsModal";
import ManageDoctrineModal from "@/Components/Modals/ManageDoctrineModal";

export const ManagePage: React.FC = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [modalState, setModalState] = useState<{
    show: boolean;
    doctrineToEdit: ManageDoctrineSchema | null;
  }>({
    show: false,
    doctrineToEdit: null,
  });

  const [skillsModalState, setSkillsModalState] = useState<{
    show: boolean;
    doctrineId: number | null;
  }>({
    show: false,
    doctrineId: null,
  });

  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.ManageDoctrines,
    queryFn: loadManageDoctrines,
  });

  const deleteMutation = useMutation({
    mutationFn: (pk: number) => deleteDoctrine(pk),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.ManageDoctrines });
    },
  });

  const handleDelete = useCallback(
    (doctrine: ManageDoctrineSchema) => {
      if (
        window.confirm(
          t('Are you sure you want to delete doctrine "{{name}}"?', {
            name: doctrine.name,
          })
        )
      ) {
        deleteMutation.mutate(doctrine.id);
      }
    },
    [t, deleteMutation]
  );

  return (
    <main>
      <ManageHeader
        onAddDoctrine={() =>
          setModalState({ show: true, doctrineToEdit: null })
        }
      />

      <Card className="border-0 shadow-sm aa-panel">
        <Card.Body className="p-3">
          <ManageDoctrinesTable
            data={data || []}
            isLoading={isLoading}
            isError={isError}
            isDeleting={deleteMutation.isPending}
            onEdit={(doc) =>
              setModalState({ show: true, doctrineToEdit: doc })
            }
            onDelete={handleDelete}
            onViewSkills={(id) =>
              setSkillsModalState({ show: true, doctrineId: id })
            }
          />
        </Card.Body>
      </Card>

      {/* Modals */}
      <ManageDoctrineModal
        show={modalState.show}
        doctrineToEdit={modalState.doctrineToEdit}
        onHide={() =>
          setModalState({ show: false, doctrineToEdit: null })
        }
      />

      <DoctrineSkillsModal
        show={skillsModalState.show}
        doctrineId={skillsModalState.doctrineId}
        onHide={() =>
          setSkillsModalState({ show: false, doctrineId: null })
        }
      />
    </main>
  );
};

export default ManagePage;
