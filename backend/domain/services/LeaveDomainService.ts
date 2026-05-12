/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Employee } from '../entities/LeaveEntity.ts';

export class LeaveDomainService {
  /**
   * Business rule: Check if employee has enough remaining leave days.
   * Cấp 3 trong chuỗi nested calls.
   */
  canApproveLeave(employee: Employee, requestedDays: number): boolean {
    if (requestedDays <= 0) return false;
    return employee.remainingLeaveDays >= requestedDays;
  }
}
