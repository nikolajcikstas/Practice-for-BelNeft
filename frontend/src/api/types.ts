export interface SkillShort {
  id: number;
  skill_id: number;
  name: string;
  category: string;
  proficiency_level: number;
}

export interface Employee {
  id: number;
  last_name: string;
  first_name: string;
  middle_name: string | null;
  position: string;
  photo_url: string | null;
  date_added: string;
  skills: SkillShort[];
}

export interface EmployeeList {
  items: Employee[];
  total: number;
  page: number;
  size: number;
}

export interface Skill {
  id: number;
  name: string;
  category: string;
}

export interface Booking {
  id: number;
  employee_id: number;
  employee_name: string | null;
  employee_photo_url: string | null;
  topic: string;
  start_time: string;
  end_time: string;
}
