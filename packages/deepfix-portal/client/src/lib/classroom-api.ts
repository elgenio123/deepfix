import { API_BASE_URL } from "./api-url";
import { getToken } from "./token";

// Helper to parse error responses
const parseErrorResponse = async (response: Response) => {
  const responseText = await response.text();
  let errorDetail = "An error occurred";
  try {
    const errorJson = JSON.parse(responseText);
    errorDetail =
      errorJson.detail ||
      errorJson.message ||
      errorJson.error ||
      `HTTP error! status: ${response.status}`;
  } catch {
    errorDetail = responseText || `HTTP error! status: ${response.status}`;
  }
  return errorDetail;
};

// Helper function to make authenticated API calls
const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> ?? {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`[API] ${options.method || "GET"} ${url}`, options.body ? JSON.parse(options.body as string) : "");

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    console.log(`[API] Response status: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      const errorDetail = await parseErrorResponse(response);
      console.error(`[API] Error:`, errorDetail);
      throw new Error(errorDetail);
    }

    const data = await response.json();
    console.log(`[API] Success:`, data);
    return data;
  } catch (error) {
    console.error(`[API] Request failed:`, error);

    // Handle network errors (server not running, CORS, etc.)
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      const networkError = `Unable to connect to the API server at ${url}. Please make sure the backend server is running at ${API_BASE_URL}.`;
      console.error(`[API] Network error:`, networkError);
      throw new Error(networkError);
    }

    // Re-throw other errors as-is
    throw error;
  }
};

// Types
export type Classroom = {
  id: string;
  name: string;
  description: string | null;
  instructor_id: string;
  instructor_name: string;
  created_at: string;
  is_active: boolean;
  member_count: number;
};

export type ClassroomCreate = {
  name: string;
  description?: string;
};

export type ClassroomUpdate = {
  name?: string;
  description?: string;
  is_active?: boolean;
};

export type ClassroomMembership = {
  id: string;
  classroom_id: string;
  student_id: string;
  student_name: string;
  student_email: string;
  joined_at: string;
  status: string;
  submission_count?: number;
};

export type ClassroomInvitation = {
  id: string;
  classroom_id: string;
  email: string;
  token: string;
  expires_at: string;
  status: string;
  created_at: string;
};

export type InvitationCreate = {
  emails: string[];
};

export type IssuePattern = {
  issue_type: string;
  count: number;
  affected_students: number;
  severity_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  example_message: string;
};

export type StudentActivity = {
  student_id: string;
  student_name: string;
  student_email: string;
  submission_count: number;
  last_submission_at: string | null;
  common_issues: string[];
};

export type ClassroomAnalytics = {
  classroom_id: string;
  classroom_name: string;
  total_students: number;
  total_submissions: number;
  issue_patterns: IssuePattern[];
  student_activities: StudentActivity[];
  time_period: {
    start: string;
    end: string;
  };
};

// Classroom CRUD operations
export async function createClassroom(data: ClassroomCreate): Promise<Classroom> {
  return await apiCall("/api/classrooms", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function listClassrooms(): Promise<Classroom[]> {
  const response = await apiCall("/api/classrooms");
  // Backend returns { items: [...], total: ... }
  return response.items || response || [];
}

export async function getClassroom(id: string): Promise<Classroom> {
  return await apiCall(`/api/classrooms/${id}`);
}

export async function updateClassroom(id: string, data: ClassroomUpdate): Promise<Classroom> {
  return await apiCall(`/api/classrooms/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteClassroom(id: string): Promise<void> {
  await apiCall(`/api/classrooms/${id}`, {
    method: "DELETE",
  });
}

// Classroom membership operations
export async function listClassroomMembers(classroomId: string): Promise<ClassroomMembership[]> {
  const response = await apiCall(`/api/classrooms/${classroomId}/members`);
  // Backend returns { items: [...], total: ... }
  return response.items || response || [];
}

export async function removeClassroomMember(classroomId: string, studentId: string): Promise<void> {
  await apiCall(`/api/classrooms/${classroomId}/members/${studentId}`, {
    method: "DELETE",
  });
}

export async function listInactiveMembers(classroomId: string): Promise<ClassroomMembership[]> {
  const response = await apiCall(`/api/classrooms/${classroomId}/members/inactive`);
  // Backend returns { items: [...], total: ... }
  return response.items || response || [];
}

export async function reactivateMember(classroomId: string, studentId: string): Promise<ClassroomMembership> {
  return await apiCall(`/api/classrooms/${classroomId}/members/${studentId}/reactivate`, {
    method: "POST",
  });
}

// Invitation operations
export async function sendClassroomInvitations(
  classroomId: string,
  data: InvitationCreate
): Promise<ClassroomInvitation[]> {
  const response = await apiCall(`/api/classrooms/${classroomId}/invitations`, {
    method: "POST",
    body: JSON.stringify(data),
  });
  // Backend returns { created: [...], failed: [...] }
  console.log(`[API] Sent invitations for classroom ${classroomId}`, response);
  // Note: Backend returns email strings in 'created', not full invitation objects
  // The actual invitations are in the database and will be fetched via listClassroomInvitations
  return response.created || response || [];
}

export async function listClassroomInvitations(classroomId: string): Promise<ClassroomInvitation[]> {
  const response = await apiCall(`/api/classrooms/${classroomId}/invitations`);
  // Backend returns { items: [...], total: ... }
  const invitations = response.items || response || [];
  console.log(`[API] Fetched ${invitations.length} invitations for classroom ${classroomId}`, invitations);
  return invitations;
}

export async function acceptInvitation(token: string): Promise<{ message: string; classroom: Classroom }> {
  return await apiCall("/api/invitations/accept", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export async function cancelInvitation(invitationId: string): Promise<void> {
  await apiCall(`/api/invitations/${invitationId}`, {
    method: "DELETE",
  });
}

export async function resendInvitation(invitationId: string): Promise<ClassroomInvitation> {
  return await apiCall(`/api/invitations/${invitationId}/resend`, {
    method: "POST",
  });
}

export async function getPendingInvitations(): Promise<ClassroomInvitation[]> {
  const response = await apiCall("/api/invitations/pending");
  // Backend returns { items: [...], total: ... }
  const invitations = response.items || response || [];
  console.log(`[API] Fetched ${invitations.length} pending invitations`, invitations);
  return invitations;
}

// Analytics operations
export async function getClassroomAnalytics(classroomId: string): Promise<ClassroomAnalytics> {
  return await apiCall(`/api/classrooms/${classroomId}/analytics`);
}

export async function getClassroomIssuePatterns(classroomId: string): Promise<IssuePattern[]> {
  return await apiCall(`/api/classrooms/${classroomId}/issue-patterns`);
}

export type StudentSubmission = {
  log_id: string;
  student_id: string;
  student_email: string;
  classroom_id: string;
  endpoint: string;
  status_code: number | null;
  duration_ms: number | null;
  created_at: string;
  issues_found: number;
  has_critical_issues: boolean;
};

export type StudentSubmissionListResponse = {
  items: StudentSubmission[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

export async function getStudentSubmissions(
  classroomId: string,
  studentId: string,
  page: number = 1,
  pageSize: number = 20
): Promise<StudentSubmissionListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  return await apiCall(`/api/classrooms/${classroomId}/students/${studentId}/submissions?${params.toString()}`);
}
