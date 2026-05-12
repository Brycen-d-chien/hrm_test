import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, Routes } from '@angular/router';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

import { LeaveRequestComponent } from './app/leave-request/leave-request.component';
import { EmployeeComponent } from './app/employee/employee.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule],
  template: `
    <div class="min-h-screen bg-slate-50">
      <nav class="bg-indigo-600 text-white p-4 font-bold flex gap-4">
        <span>HRM System</span>
        <a routerLink="/employees" class="hover:underline">Employees</a>
        <a routerLink="/leave/1" class="hover:underline">Leave Request #1</a>
      </nav>
      <div class="p-6">
        <router-outlet></router-outlet>
      </div>
    </div>
  `
})
export class AppComponent {}

const routes: Routes = [
  { path: 'employees', component: EmployeeComponent },
  { path: 'leave/:id', component: LeaveRequestComponent },
  { path: '', redirectTo: '/employees', pathMatch: 'full' }
];

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(),
    provideRouter(routes)
  ]
}).catch(err => console.error(err));
