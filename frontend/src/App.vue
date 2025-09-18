<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar__brand">
        <span class="topbar__logo">LiteHIS</span>
        <span class="topbar__subtitle">虎门医院门诊驾驶舱</span>
      </div>
      <div class="topbar__meta">
        <span class="topbar__meta-item">今日概览</span>
        <span class="topbar__meta-item">{{ now }}</span>
      </div>
    </header>

    <main class="content">
      <section class="summary-grid">
        <article
          v-for="card in summaryCards"
          :key="card.label"
          class="summary-card"
          :style="{ '--accent': card.accent }"
        >
          <p class="summary-card__label">{{ card.label }}</p>
          <p class="summary-card__value">{{ card.value }}</p>
        </article>
      </section>

      <section class="grid">
        <SectionCard title="登记新患者" subtitle="采集患者基础信息">
          <form class="form-grid" @submit.prevent="handleCreatePatient">
            <label>
              姓名
              <input v-model="patientForm.full_name" placeholder="例如：张小雅" required />
            </label>
            <label>
              性别
              <select v-model="patientForm.gender">
                <option value="female">女</option>
                <option value="male">男</option>
                <option value="other">其他</option>
                <option value="unknown">未知</option>
              </select>
            </label>
            <label>
              出生日期
              <input v-model="patientForm.birth_date" type="date" />
            </label>
            <label>
              联系电话
              <input v-model="patientForm.phone" placeholder="138xxxxxxx" />
            </label>
            <label class="form-grid__full">
              联系地址
              <input v-model="patientForm.address" placeholder="患者常住地址" />
            </label>
            <button class="button" type="submit">保存患者</button>
          </form>
        </SectionCard>

        <SectionCard title="新增医生" subtitle="维护门诊出诊信息">
          <form class="form-grid" @submit.prevent="handleCreateDoctor">
            <label>
              姓名
              <input v-model="doctorForm.full_name" placeholder="例如：李主任" required />
            </label>
            <label>
              职称
              <input v-model="doctorForm.title" placeholder="主任医师" />
            </label>
            <label>
              所属科室
              <select v-model="doctorForm.department_id">
                <option :value="null">未分配</option>
                <option v-for="department in departments" :key="department.id" :value="department.id">
                  {{ department.name }}
                </option>
              </select>
            </label>
            <label>
              专长
              <input v-model="doctorForm.specialty" placeholder="呼吸内科、儿童哮喘…" />
            </label>
            <label>
              联系电话
              <input v-model="doctorForm.phone" placeholder="132xxxxxxx" />
            </label>
            <button class="button" type="submit">保存医生</button>
          </form>
        </SectionCard>

        <SectionCard title="安排门诊预约" subtitle="匹配医生排班和患者需求">
          <form class="form-grid" @submit.prevent="handleCreateAppointment">
            <label>
              患者
              <select v-model.number="appointmentForm.patient_id" required>
                <option value="" disabled>请选择患者</option>
                <option v-for="patient in patients" :key="patient.id" :value="patient.id">
                  {{ patient.full_name }}
                </option>
              </select>
            </label>
            <label>
              医生
              <select v-model.number="appointmentForm.doctor_id" required>
                <option value="" disabled>请选择医生</option>
                <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                  {{ doctor.full_name }}
                </option>
              </select>
            </label>
            <label>
              预约时间
              <input v-model="appointmentForm.scheduled_time" type="datetime-local" required />
            </label>
            <label class="form-grid__full">
              就诊事由
              <input v-model="appointmentForm.reason" placeholder="症状或备注信息" />
            </label>
            <button class="button" type="submit">创建预约</button>
          </form>
        </SectionCard>

        <SectionCard title="新增科室" subtitle="为医生归属科室">
          <form class="form-grid" @submit.prevent="handleCreateDepartment">
            <label>
              科室名称
              <input v-model="departmentForm.name" placeholder="例如：呼吸内科" required />
            </label>
            <label class="form-grid__full">
              科室简介
              <input v-model="departmentForm.description" placeholder="科室诊疗范围" />
            </label>
            <button class="button" type="submit">保存科室</button>
          </form>
        </SectionCard>
      </section>

      <section class="grid grid--wide">
        <SectionCard title="最新登记患者" subtitle="展示最近 10 条记录">
          <ul class="list">
            <li v-for="patient in patients" :key="patient.id" class="list__item">
              <div>
                <p class="list__title">{{ patient.full_name }}</p>
                <p class="list__subtitle">
                  {{ formatDate(patient.created_at) }} · {{ genderMap[patient.gender] || "未知" }}
                </p>
              </div>
              <span class="list__tag">#{{ patient.id }}</span>
            </li>
            <li v-if="!patients.length" class="list__item list__item--empty">暂无患者数据</li>
          </ul>
        </SectionCard>

        <SectionCard title="即将到诊预约" subtitle="按照时间排序">
          <ul class="list">
            <li v-for="appointment in upcomingAppointments" :key="appointment.id" class="list__item">
              <div>
                <p class="list__title">{{ appointment.patient.full_name }}</p>
                <p class="list__subtitle">
                  {{ formatDateTime(appointment.scheduled_time) }} · {{ appointment.doctor.full_name }}
                </p>
              </div>
              <span class="status-pill" :data-status="appointment.status">{{ statusMap[appointment.status] }}</span>
            </li>
            <li v-if="!upcomingAppointments.length" class="list__item list__item--empty">暂无预约信息</li>
          </ul>
        </SectionCard>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { apiClient, type AppointmentPayload, type DoctorPayload, type PatientPayload } from "./api";
import SectionCard from "./components/SectionCard.vue";

type Gender = "female" | "male" | "other" | "unknown";

type AppointmentStatus = "scheduled" | "completed" | "cancelled";

interface Patient {
  id: number;
  full_name: string;
  gender: Gender;
  birth_date?: string | null;
  phone?: string | null;
  address?: string | null;
  created_at: string;
}

interface Department {
  id: number;
  name: string;
  description?: string | null;
}

interface Doctor {
  id: number;
  full_name: string;
  title?: string | null;
  specialty?: string | null;
  phone?: string | null;
  department?: Department | null;
}

interface Appointment {
  id: number;
  scheduled_time: string;
  status: AppointmentStatus;
  reason?: string | null;
  patient: Patient;
  doctor: Doctor;
  created_at: string;
}

interface Summary {
  total_patients: number;
  total_doctors: number;
  appointments_today: number;
  upcoming_appointments: number;
  active_departments: number;
}

const now = new Intl.DateTimeFormat("zh-CN", {
  dateStyle: "medium",
  timeStyle: "short",
}).format(new Date());

const summary = ref<Summary | null>(null);
const patients = ref<Patient[]>([]);
const doctors = ref<Doctor[]>([]);
const departments = ref<Department[]>([]);
const appointments = ref<Appointment[]>([]);

const genderMap: Record<Gender, string> = {
  female: "女",
  male: "男",
  other: "其他",
  unknown: "未知",
};

const statusMap: Record<AppointmentStatus, string> = {
  scheduled: "待就诊",
  completed: "已完成",
  cancelled: "已取消",
};

const patientForm = reactive<PatientPayload>({
  full_name: "",
  gender: "female",
  birth_date: "",
  phone: "",
  id_card: "",
  address: "",
});

const doctorForm = reactive<DoctorPayload>({
  full_name: "",
  title: "",
  department_id: null,
  specialty: "",
  phone: "",
});

const appointmentForm = reactive<AppointmentPayload>({
  patient_id: 0,
  doctor_id: 0,
  scheduled_time: "",
  reason: "",
});

const departmentForm = reactive({
  name: "",
  description: "",
});

const summaryCards = computed(() => [
  {
    label: "患者总数",
    value: summary.value?.total_patients ?? 0,
    accent: "#6366f1",
  },
  {
    label: "医生总数",
    value: summary.value?.total_doctors ?? 0,
    accent: "#22c55e",
  },
  {
    label: "今日预约",
    value: summary.value?.appointments_today ?? 0,
    accent: "#f97316",
  },
  {
    label: "待诊队列",
    value: summary.value?.upcoming_appointments ?? 0,
    accent: "#0ea5e9",
  },
]);

const upcomingAppointments = computed(() =>
  appointments.value
    .filter((item) => new Date(item.scheduled_time).getTime() >= Date.now())
    .slice(0, 8)
);

function resetPatientForm() {
  patientForm.full_name = "";
  patientForm.gender = "female";
  patientForm.birth_date = "";
  patientForm.phone = "";
  patientForm.id_card = "";
  patientForm.address = "";
}

function resetDoctorForm() {
  doctorForm.full_name = "";
  doctorForm.title = "";
  doctorForm.department_id = null;
  doctorForm.specialty = "";
  doctorForm.phone = "";
}

function resetAppointmentForm() {
  appointmentForm.patient_id = 0;
  appointmentForm.doctor_id = 0;
  appointmentForm.scheduled_time = "";
  appointmentForm.reason = "";
}

function resetDepartmentForm() {
  departmentForm.name = "";
  departmentForm.description = "";
}

async function loadSummary() {
  const { data } = await apiClient.get<Summary>("/dashboard/summary");
  summary.value = data;
}

async function loadPatients() {
  const { data } = await apiClient.get<Patient[]>("/patients");
  patients.value = data.slice(0, 10);
}

async function loadDoctors() {
  const { data } = await apiClient.get<Doctor[]>("/doctors");
  doctors.value = data;
}

async function loadAppointments() {
  const { data } = await apiClient.get<Appointment[]>("/appointments", {
    params: { status: "scheduled" },
  });
  appointments.value = data;
}

async function loadDepartments() {
  const { data } = await apiClient.get<Department[]>("/departments");
  departments.value = data;
}

async function handleCreatePatient() {
  await apiClient.post("/patients", patientForm);
  resetPatientForm();
  await Promise.all([loadPatients(), loadSummary()]);
}

async function handleCreateDoctor() {
  const payload = { ...doctorForm, department_id: doctorForm.department_id ?? null };
  await apiClient.post("/doctors", payload);
  resetDoctorForm();
  await Promise.all([loadDoctors(), loadSummary()]);
}

async function handleCreateAppointment() {
  await apiClient.post("/appointments", appointmentForm);
  resetAppointmentForm();
  await Promise.all([loadAppointments(), loadSummary()]);
}

async function handleCreateDepartment() {
  await apiClient.post("/departments", departmentForm);
  resetDepartmentForm();
  await Promise.all([loadDepartments(), loadSummary()]);
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("zh-CN", { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(value)
  );
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

onMounted(async () => {
  await Promise.all([loadSummary(), loadDepartments(), loadDoctors(), loadPatients(), loadAppointments()]);
});
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 1.5rem 2rem 3rem;
  gap: 2rem;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-radius: 20px;
  background: radial-gradient(circle at top left, #4f46e5, #1e3a8a);
  color: #ffffff;
  box-shadow: 0 20px 40px rgba(51, 65, 255, 0.2);
}

.topbar__brand {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.topbar__logo {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.topbar__subtitle {
  font-size: 0.95rem;
  opacity: 0.85;
}

.topbar__meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.9rem;
  opacity: 0.9;
}

.topbar__meta-item {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.15);
}

.content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.summary-card {
  background: #fff;
  border-radius: 18px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.16);
  border-top: 6px solid var(--accent, #6366f1);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-card__label {
  margin: 0;
  font-size: 0.95rem;
  color: #475569;
}

.summary-card__value {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
}

.grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.grid--wide {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: #1f2937;
}

.form-grid input,
.form-grid select {
  border-radius: 10px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  padding: 0.6rem 0.75rem;
  font-size: 0.95rem;
  background: rgba(255, 255, 255, 0.95);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-grid input:focus,
.form-grid select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
}

.form-grid__full {
  grid-column: 1 / -1;
}

.button {
  grid-column: 1 / -1;
  padding: 0.75rem 1rem;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: white;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(99, 102, 241, 0.3);
}

.list {
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  list-style: none;
  gap: 0.75rem;
}

.list__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.list__item--empty {
  justify-content: center;
  color: #94a3b8;
  font-style: italic;
}

.list__title {
  margin: 0;
  font-weight: 600;
  color: #0f172a;
}

.list__subtitle {
  margin: 0.35rem 0 0;
  font-size: 0.85rem;
  color: #475569;
}

.list__tag {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background: rgba(79, 70, 229, 0.15);
  color: #4338ca;
  font-size: 0.8rem;
}

.status-pill {
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-pill[data-status="scheduled"] {
  background: rgba(59, 130, 246, 0.12);
  color: #1d4ed8;
}

.status-pill[data-status="completed"] {
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
}

.status-pill[data-status="cancelled"] {
  background: rgba(248, 113, 113, 0.12);
  color: #b91c1c;
}

@media (max-width: 768px) {
  .app-shell {
    padding: 1.25rem 1rem 2rem;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
