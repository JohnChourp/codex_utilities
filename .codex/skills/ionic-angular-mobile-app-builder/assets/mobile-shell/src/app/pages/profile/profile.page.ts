import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import {
  IonBackButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonItem,
  IonLabel,
  IonList,
  IonNote,
  IonTitle,
  IonToggle,
  IonToolbar,
} from "@ionic/angular/standalone";

@Component({
  selector: "app-profile-page",
  standalone: true,
  imports: [
    CommonModule,
    IonBackButton,
    IonButtons,
    IonContent,
    IonHeader,
    IonItem,
    IonLabel,
    IonList,
    IonNote,
    IonTitle,
    IonToggle,
    IonToolbar,
  ],
  templateUrl: "./profile.page.html",
  styleUrl: "./profile.page.scss",
})
export class ProfilePage {
  public preferences = [
    {
      title: "Contextual alerts",
      detail: "Show timely nudges based on recent activity and likely next steps.",
      enabled: true,
    },
    {
      title: "Quiet mode",
      detail: "Reduce interruptions and keep the experience calm during focused sessions.",
      enabled: false,
    },
    {
      title: "Saved progress",
      detail: "Restore the last viewed step of the __PROJECT_TYPE__ flow on launch.",
      enabled: true,
    },
  ];
}
