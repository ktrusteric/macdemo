export enum UserRole {
    FREE = "free",
    PAID = "paid",
    ADMIN = "admin"
  }
  
  export interface User {
    id: string;
    email: string;
    username: string;
    role: UserRole;
    is_active: boolean;
    created_at: string;
    has_initial_tags: boolean;
    access_features: string[];
  }
  
  export interface UserRegistration {
    email: string;
    username: string;
    password: string;
    confirm_password?: string;
    initial_regions: string[];
    initial_energy_types: string[];
  }
  
  export interface UserLogin {
    email: string;
    password: string;
  }