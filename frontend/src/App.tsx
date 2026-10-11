// React
import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "i18next";
import Backend from "i18next-http-backend";
import { NuqsAdapter } from "nuqs/adapters/react-router/v8";
import { initReactI18next } from "react-i18next";

// AA corptools_doctrine
import { AppName, ProjectName } from "@/configuration";
import { ErrorPage } from "@/Pages/404";
import AuthBase from "@/Pages/Base";
import CorporationDoctrinesPage from "@/Pages/CorporationDoctrinesPage";
import DoctrinesPage from "@/Pages/DoctrinesPage";
import ManagePage from "@/Pages/ManagePage";
import OverviewPage from "@/Pages/OverviewPage";

const queryClient = new QueryClient();

// Read language directly from Django's LANGUAGE_CODE (set as lang="..." on root div)
const djangoLanguage =
  typeof document !== "undefined"
    ? document.getElementById(`${AppName}-root`)?.getAttribute("lang") ?? "en"
    : "en";

i18n
  .use(Backend)
  .use(initReactI18next)
  .init({
    lng: djangoLanguage,
    fallbackLng: "en",
    keySeparator: false,
    nsSeparator: false,
    interpolation: {
      escapeValue: false,
    },
    react: {
      useSuspense: false,
    },
    backend: {
      loadPath: `/static/${ProjectName}/i18n/{{lng}}/{{ns}}.json`,
    },
  });

function App() {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <NuqsAdapter>
            <Routes>
              <Route path={`/${ProjectName}/`} element={<AuthBase />}>
                <Route index element={<DoctrinesPage />} />
                <Route path="doctrine/" element={<DoctrinesPage />} />
                <Route path="doctrine/:characterId/" element={<DoctrinesPage />} />
                <Route path="corporation/" element={<CorporationDoctrinesPage />} />
                <Route
                  path="corporation/:corporationId/"
                  element={<CorporationDoctrinesPage />}
                />
                <Route path="overview/" element={<OverviewPage />} />
                <Route path="manage/" element={<ManagePage />} />
                <Route path="*" element={<ErrorPage />} />
              </Route>
              <Route
                path="*"
                element={<Navigate to={`/${ProjectName}/`} replace />}
              />
            </Routes>
          </NuqsAdapter>
        </BrowserRouter>
      </QueryClientProvider>
    </React.StrictMode>
  );
}

export default App;
