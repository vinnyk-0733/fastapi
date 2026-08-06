import React from "react";
import { render, screen } from "@testing-library/react";
import TaglineSection from "./TaglineSection";

test("renders TaglineSection component with title and tagline content", () => {
  render(<TaglineSection />);
  
  // Check main heading
  const headingElement = screen.getByText(/Track\. Manage\. Grow\./i);
  expect(headingElement).toBeInTheDocument();

  // Check tagline text
  const taglineElement = screen.getByText(/Streamline your inventory with smart product management/i);
  expect(taglineElement).toBeInTheDocument();

  // Check company badge
  expect(screen.getByText(/Powered by/i)).toBeInTheDocument();
  expect(screen.getByText(/Telusko/i)).toBeInTheDocument();
});
