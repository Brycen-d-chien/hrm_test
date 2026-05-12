import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

interface Employee {
    id: number;
    name: string;
    role: string;
    remaining_leave_days: number;
}

@Component({
    selector: 'app-employee',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="p-6 bg-white border border-slate-200 rounded-xl shadow-sm">
        <h2 class="text-xl font-bold mb-4 text-slate-800">Employee Management</h2>
        
        <div class="mb-4">
            <button (click)="loadEmployees(true)" class="px-4 py-2 bg-blue-600 text-white rounded text-sm font-bold shadow-sm hover:bg-blue-700 mr-2">Load As Admin</button>
            <button (click)="loadEmployees(false)" class="px-4 py-2 border border-slate-300 rounded text-sm font-bold shadow-sm hover:bg-slate-50">Load My Info (Employee)</button>
        </div>

        <div *ngIf="loading" class="text-slate-500">Loading...</div>
        <div *ngIf="error" class="text-red-500">{{ error }}</div>

        <ul class="divide-y divide-slate-100" *ngIf="!loading && employees.length > 0">
            <li *ngFor="let emp of employees" class="py-3 flex justify-between">
                <div>
                    <p class="font-bold text-slate-800">{{ emp.name }}</p>
                    <p class="text-xs text-slate-500">Role: {{ emp.role }}</p>
                </div>
                <div class="text-right">
                    <p class="text-sm font-medium">{{ emp.remaining_leave_days }} days left</p>
                </div>
            </li>
        </ul>
    </div>
    `
})
export class EmployeeComponent implements OnInit {
    employees: Employee[] = [];
    loading = false;
    error = '';
    
    private http = inject(HttpClient);

    ngOnInit() {}

    loadEmployees(isAdmin: boolean) {
        this.loading = true;
        this.error = '';
        const url = isAdmin ? '/api/employees/' : '/api/employees/me';
        const headers = { 'x-user-role': isAdmin ? 'Admin' : 'Employee' }; // Mock Auth Header

        this.http.get<any>(url, { headers }).subscribe({
            next: (data) => {
                this.employees = Array.isArray(data) ? data : [data];
                this.loading = false;
            },
            error: (err) => {
                this.error = err.error?.detail || 'Lỗi server';
                this.loading = false;
                this.employees = [];
            }
        });
    }
}
