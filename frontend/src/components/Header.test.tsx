import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Header } from "../components/Header";

describe("Header Component", () => {
  it("renders the header with correct title", () => {
    render(<Header onLogout={() => {}} userData={{}} />);

    const titleElement = screen.getByText(/Panel de Control/i);
    expect(titleElement).toBeInTheDocument();
  });

  it("renders navigation links", () => {
    render(<Header onLogout={() => {}} userData={{}} />);

    const inicioLink = screen.getByText(/Inicio/i);
    const perfilLink = screen.getByText(/Perfil/i);
    const configuracionLink = screen.getByText(/Configuración/i);

    expect(inicioLink).toBeInTheDocument();
    expect(perfilLink).toBeInTheDocument();
    expect(configuracionLink).toBeInTheDocument();
  });

  it("has correct accessibility attributes", () => {
    render(<Header onLogout={() => {}} userData={{}} />);

    const navElement = screen.getByRole("navigation");
    expect(navElement).toBeInTheDocument();
  });
});
