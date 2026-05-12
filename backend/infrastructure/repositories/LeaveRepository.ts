/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { LeaveRequest, Employee, LeaveStatus } from '../../domain/entities/LeaveEntity.ts';

// Mock DB Storage
const MOCK_LEAVE_REQUESTS: LeaveRequest[] = [
  {
    id: 'lr-1',
    employeeId: 'emp-1',
    startDate: '2026-06-01',
    endDate: '2026-06-03',
    days: 3,
    status: LeaveStatus.PENDING,
    reason: 'Family vacation'
  }
];

const MOCK_EMPLOYEES: Employee[] = [
  { id: 'emp-1', name: 'John Doe', role: 'Employee', remainingLeaveDays: 10 },
  { id: 'admin-1', name: 'Admin User', role: 'Admin', remainingLeaveDays: 20 }
];

export class LeaveRepository {
  private leaveRequests = MOCK_LEAVE_REQUESTS;
  private employees = MOCK_EMPLOYEES;

  /**
   * Cấp 4: Truy cập dữ liệu
   */
  async getLeaveRequestById(id: string): Promise<LeaveRequest | null> {
    return this.leaveRequests.find(lr => lr.id === id) || null;
  }

  async getEmployeeById(id: string): Promise<Employee | null> {
    return this.employees.find(emp => emp.id === id) || null;
  }

  async getLeaveRequests(): Promise<LeaveRequest[]> {
    return this.leaveRequests;
  }

  async updateLeaveStatus(id: string, status: LeaveStatus): Promise<void> {
    const lr = this.leaveRequests.find(req => req.id === id);
    if (lr) {
      lr.status = status;
    }
  }

  async updateEmployeeRemainingDays(id: string, daysToSubtract: number): Promise<void> {
    const emp = this.employees.find(e => e.id === id);
    if (emp) {
      emp.remainingLeaveDays -= daysToSubtract;
    }
  }

  async createLeaveRequest(request: LeaveRequest): Promise<void> {
    this.leaveRequests.push(request);
  }
}
