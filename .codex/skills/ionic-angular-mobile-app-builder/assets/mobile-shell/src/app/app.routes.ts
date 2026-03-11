import { Routes } from "@angular/router";

export const routes: Routes = [
  {
    path: "",
    loadComponent: () =>
      import("./pages/home/home.page").then((module) => module.HomePage),
  },
  {
    path: "discover",
    loadComponent: () =>
      import("./pages/discover/discover.page").then((module) => module.DiscoverPage),
  },
  {
    path: "profile",
    loadComponent: () =>
      import("./pages/profile/profile.page").then((module) => module.ProfilePage),
  },
  {
    path: "**",
    redirectTo: "",
  },
];
