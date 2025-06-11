export interface Level {
  total: number;
  price: number;
  salary: number;
  recruitment_h1: number;
  recruitment_h2: number;
  churn_h1: number;
  churn_h2: number;
  growth_h1: number;
  growth_h2: number;
}

export interface Office {
  name: string;
  total_fte: number;
  levels: Record<string, Level>;
  operations: {
    total: number;
    price: number;
    salary: number;
    recruitment_h1: number;
    recruitment_h2: number;
    churn_h1: number;
    churn_h2: number;
    growth_h1: number;
    growth_h2: number;
  };
} 