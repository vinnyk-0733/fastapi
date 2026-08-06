import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import axios from "axios";

jest.mock("axios", () => {
  const instance = {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  };
  return {
    create: jest.fn(() => instance),
    ...instance,
  };
});

import App from "./App";

const mockAxiosInstance = axios.create();

const mockProducts = [
  { id: 1, name: "phone", description: "budget phone", price: 99, quantity: 10 },
  { id: 2, name: "laptop", description: "gaming laptop", price: 999, quantity: 6 },
];

describe("App Component", () => {
  beforeEach(() => {
    mockAxiosInstance.get.mockReset();
    mockAxiosInstance.post.mockReset();
    mockAxiosInstance.put.mockReset();
    mockAxiosInstance.delete.mockReset();

    mockAxiosInstance.get.mockResolvedValue({ data: mockProducts });
  });

  test("renders header title and stats", async () => {
    render(<App />);

    expect(screen.getByText("Telusko Trac")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Total: 2")).toBeInTheDocument();
    });

    expect(screen.getByText("phone")).toBeInTheDocument();
    expect(screen.getByText("laptop")).toBeInTheDocument();
  });

  test("filters products based on search input", async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("phone")).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Search by id, name or description.../i);
    fireEvent.change(searchInput, { target: { value: "laptop" } });

    expect(screen.queryByText("phone")).not.toBeInTheDocument();
    expect(screen.getByText("laptop")).toBeInTheDocument();
  });

  test("adds a new product via form submission", async () => {
    mockAxiosInstance.post.mockResolvedValueOnce({
      data: { id: 3, name: "keyboard", description: "mechanical keyboard", price: 50, quantity: 20 },
    });
    mockAxiosInstance.get
      .mockResolvedValueOnce({ data: mockProducts })
      .mockResolvedValueOnce({
        data: [
          ...mockProducts,
          { id: 3, name: "keyboard", description: "mechanical keyboard", price: 50, quantity: 20 },
        ],
      });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Total: 2")).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText("ID"), { target: { value: "3" } });
    fireEvent.change(screen.getByPlaceholderText("Name"), { target: { value: "keyboard" } });
    fireEvent.change(screen.getByPlaceholderText("Description"), { target: { value: "mechanical keyboard" } });
    fireEvent.change(screen.getByPlaceholderText("Price"), { target: { value: "50" } });
    fireEvent.change(screen.getByPlaceholderText("Quantity"), { target: { value: "20" } });

    const addButton = screen.getByRole("button", { name: /^Add$/i });
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(mockAxiosInstance.post).toHaveBeenCalledWith("/products/", {
        id: 3,
        name: "keyboard",
        description: "mechanical keyboard",
        price: 50,
        quantity: 20,
      });
    });

    await waitFor(() => {
      expect(screen.getByText("Product created successfully")).toBeInTheDocument();
    });
  });

  test("edits an existing product", async () => {
    mockAxiosInstance.put.mockResolvedValueOnce({ data: "Product updated" });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("phone")).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole("button", { name: /Edit/i });
    fireEvent.click(editButtons[0]); // Edit 'phone'

    expect(screen.getByText("Edit Product")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Name").value).toBe("phone");

    fireEvent.change(screen.getByPlaceholderText("Name"), { target: { value: "phone Pro" } });

    const updateButton = screen.getByRole("button", { name: /^Update$/i });
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(mockAxiosInstance.put).toHaveBeenCalledWith("/products/1", expect.objectContaining({
        name: "phone Pro",
      }));
    });
  });

  test("deletes a product", async () => {
    window.confirm = jest.fn().mockReturnValue(true);
    mockAxiosInstance.delete.mockResolvedValueOnce({ data: "Product deleted" });
    mockAxiosInstance.get
      .mockResolvedValueOnce({ data: mockProducts })
      .mockResolvedValueOnce({ data: [mockProducts[1]] });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("phone")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button", { name: /Delete/i });
    fireEvent.click(deleteButtons[0]); // Delete 'phone'

    await waitFor(() => {
      expect(mockAxiosInstance.delete).toHaveBeenCalledWith("/products/1");
    });
  });
});
