import { useState, useEffect } from "react";
import { apiService } from "../services/api";
import type { ProtectedResponse } from "../types/api";
import { showToast } from "./Toast";
import { Header } from "./Header";
import { UserProfile } from "./UserProfile";
import ProjectDashboard from "./ProjectDashboard";

interface ReserveStudyDashboardProps {
  onLogout: () => void;
}

export const ReserveStudyDashboard = ({
  onLogout,
}: ReserveStudyDashboardProps) => {
  const [userData, setUserData] = useState<ProtectedResponse | null>(null);
  // Users list intentionally omitted from UI for now; simplify state
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<"overview" | "projects">(
    "overview",
  );

  useEffect(() => {
    const fetchData = async () => {
      try {
        const protectedData = await apiService.getProtectedData();
        setUserData(protectedData);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else if (
          typeof err === "object" &&
          err !== null &&
          "response" in err
        ) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const e = err as any;
          setError(e?.response?.data?.detail ?? "Error al cargar los datos");
        } else {
          setError(String(err));
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    showToast.success("Sesión cerrada correctamente");
    onLogout();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner-lg mx-auto mb-4"></div>
          <p className="text-body text-secondary-300">Cargando datos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="container-compact">
          <div className="panel-elevated responsive-padding text-center">
            <div className="mb-6">
              <div className="text-error-400 text-4xl mb-4">❌</div>
              <h2 className="text-heading text-2xl text-error-400 mb-2">
                Error de conexión
              </h2>
              <p className="text-body text-secondary-300">{error}</p>
            </div>
            <button onClick={handleLogout} className="btn-primary">
              Volver al login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header onLogout={handleLogout} userData={userData} />

      <main className="flex-1">
        {/* Navigation Tabs */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex space-x-8">
              <button
                onClick={() => setCurrentView("overview")}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  currentView === "overview"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setCurrentView("projects")}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  currentView === "projects"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Reserve Studies
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        {currentView === "overview" ? (
          <div className="container-fluid section">
            <div className="space-y-8">
              {/* Sección de perfil de usuario */}
              <section className="fade-in">
                <UserProfile userData={userData} />
              </section>

              {/* Welcome message for Reserve Flow AI */}
              <section className="fade-in">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
                  <h2 className="text-3xl font-bold mb-4">
                    Welcome to Reserve Flow AI
                  </h2>
                  <p className="text-xl mb-6">
                    Professional reserve study management made simple. Create
                    projects, track components, and analyze your reserve fund
                    health with powerful analytics.
                  </p>
                  <button
                    onClick={() => setCurrentView("projects")}
                    className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                  >
                    Get Started with Projects
                  </button>
                </div>
              </section>
            </div>
          </div>
        ) : (
          <ProjectDashboard />
        )}
      </main>
    </div>
  );
};
