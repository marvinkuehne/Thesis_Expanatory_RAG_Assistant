import { useState } from "react";
import api from "../../api.ts";
import type { CatOption } from "../../types/categories.ts"; // oder dein zentraler Typ

export function useCategories(userId: string | null) {
  const [categories, setCategories] = useState<CatOption[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<CatOption[]>([]);

  async function loadCategories() {
    if (!userId) return;
    const res = await api.get(`/get_category/${userId}`);
    setCategories(res.data.categories.map((c: string) => ({ value: c, label: c })));
  }

  return {
    categories,
    selectedCategories,
    setSelectedCategories,
    loadCategories,
  };
}