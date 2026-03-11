import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import {
  IonBackButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonIcon,
  IonTitle,
  IonToolbar,
} from "@ionic/angular/standalone";
import {
  bookmarkOutline,
  flashOutline,
  layersOutline,
  leafOutline,
} from "ionicons/icons";

@Component({
  selector: "app-discover-page",
  standalone: true,
  imports: [
    CommonModule,
    IonBackButton,
    IonButtons,
    IonContent,
    IonHeader,
    IonIcon,
    IonTitle,
    IonToolbar,
  ],
  templateUrl: "./discover.page.html",
  styleUrl: "./discover.page.scss",
})
export class DiscoverPage {
  public cards = [
    {
      title: "Starter journeys",
      copy: "Turn the first actions of __PROJECT_TYPE__ into a simple guided path with clear progress cues.",
      icon: layersOutline,
    },
    {
      title: "Fast feedback loops",
      copy: "Use digest cards, reminders, and lightweight summaries to keep users moving without friction.",
      icon: flashOutline,
    },
    {
      title: "Useful saves",
      copy: "Highlight the actions or items people want to return to most often with obvious touch targets.",
      icon: bookmarkOutline,
    },
    {
      title: "Calm visual language",
      copy: "Balanced contrast, generous spacing, and rounded surfaces keep the shell friendly on mobile.",
      icon: leafOutline,
    },
  ];
}
