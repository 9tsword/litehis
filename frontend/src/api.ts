import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface PatientPayload {
  full_name: string;
  gender?: string;
  birth_date?: string | null;
  phone?: string | null;
  id_card?: string | null;
  address?: string | null;
}

export interface DoctorPayload {
  full_name: string;
  title?: string | null;
  department_id?: number | null;
  specialty?: string | null;
  phone?: string | null;
}

export interface AppointmentPayload {
  patient_id: number;
  doctor_id: number;
  scheduled_time: string;
  reason?: string | null;
}
