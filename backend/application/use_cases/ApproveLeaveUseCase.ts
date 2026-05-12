/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { LeaveRepository } from '../../infrastructure/repositories/LeaveRepository.ts';
import { LeaveDomainService } from '../../domain/services/LeaveDomainService.ts';
import { LeaveStatus } from '../../domain/entities/LeaveEntity.ts';

export class ApproveLeaveUseCase {
  constructor(
    private leaveRepo: LeaveRepository,
    private leaveDomainService: LeaveDomainService
  ) {}

  /**
   * Cấp 2: Điều phối logic (Orchestration)
   */
  async execute(leaveRequestId: string): Promise<{ success: boolean; message: string }> {
    // 1. Lấy thông tin đơn (Infrastructure Level)
    const leaveRequest = await this.leaveRepo.getLeaveRequestById(leaveRequestId);
    if (!leaveRequest) {
      return { success: false, message: 'Leave request not found' };
    }

    if (leaveRequest.status !== LeaveStatus.PENDING) {
      return { success: false, message: 'Leave request is already processed' };
    }

    // 2. Lấy thông tin nhân viên
    const employee = await this.leaveRepo.getEmployeeById(leaveRequest.employeeId);
    if (!employee) {
      return { success: false, message: 'Employee not found' };
    }

    // 3. Kiểm tra Business Rule (Domain Service Level)
    const canApprove = this.leaveDomainService.canApproveLeave(employee, leaveRequest.days);
    if (!canApprove) {
      return { success: false, message: 'Insufficient leave balance' };
    }

    // 4. Lưu thay đổi (Infrastructure Level)
    await this.leaveRepo.updateLeaveStatus(leaveRequestId, LeaveStatus.APPROVED);
    await this.leaveRepo.updateEmployeeRemainingDays(employee.id, leaveRequest.days);

    return { success: true, message: 'Leave request approved successfully' };
  }
}
