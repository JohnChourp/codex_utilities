import { CommonModule } from "@angular/common";
import { Component } from "@angular/core";
import { RouterLink } from "@angular/router";
import {
  IonButton,
  IonContent,
  IonHeader,
  IonIcon,
  IonTitle,
  IonToolbar,
} from "@ionic/angular/standalone";
import {
  analyticsOutline,
  arrowForwardOutline,
  compassOutline,
  pulseOutline,
  sparklesOutline,
} from "ionicons/icons";

@Component({
  selector: "app-home-page",
  standalone: true,
  imports: [
    CommonModule,
    IonButton,
    IonContent,
    IonHeader,
    IonIcon,
    IonTitle,
    IonToolbar,
    RouterLink,
  ],
  templateUrl: "./home.page.html",
  styleUrl: "./home.page.scss",
})
export class HomePage {
  public heroIcon = sparklesOutline;
  public ctaIcon = arrowForwardOutline;

  public stats = [
    {
      label: "Momentum",
      value: "24%",
      detail: "More weekly engagement",
      icon: analyticsOutline,
    },
    {
      label: "Focus",
      value: "08",
      detail: "Priority actions surfaced",
      icon: compassOutline,
    },
    {
      label: "Energy",
      value: "4.9",
      detail: "Average user delight score",
      icon: pulseOutline,
    },
  ];

  public highlights = [
    {
      title: "__INSIGHT_TITLE__",
      copy: "__INSIGHT_BODY__",
    },
    {
      title: "Quick pathways",
      copy: "Keep the next step obvious with large touch targets and one-thumb navigation.",
    },
    {
      title: "Native-ready setup",
      copy: "Build once, then sync straight into Android and iOS without reworking the UI shell.",
    },
  ];
}
