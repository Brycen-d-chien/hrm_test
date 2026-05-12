/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export enum LeaveStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED'
}

export interface LeaveRequest {
  id: string;
  employeeId: string;
  startDate: string;
  endDate: string;
  days: number;
  status: LeaveStatus;
  reason: string;
}

export interface Employee {
  id: string;
  name: string;
  role: 'Admin' | 'Employee';
  remainingLeaveDays: number;
}
