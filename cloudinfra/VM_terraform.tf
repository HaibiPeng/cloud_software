terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.5.0"
    }
  }
}

provider "google" {
  project = "compelling-mesh-326115" // project id
  region  = "europe-north1"
  zone    = "europe-north1-a"
}

// add public/external/static ip address
resource "google_compute_address" "static" {
  name = "ipv4-address"
}

resource "google_compute_instance" "vm-instance" {
  name         = var.vm_name_input
  machine_type = "e2-standard-2"

  // define os image type
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  // define network
  network_interface {
    network = "default"
    access_config {
        nat_ip = google_compute_address.static.address
    }
  }
}

// allow ssh
resource "google_compute_firewall" "ssh-rule" {
  name    = "ssh"
  network = "default"
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  target_tags   = ["vm-instance"]
  source_ranges = ["0.0.0.0/0"]
}

// to name the vm through cmd input
variable "vm_name_input" {
  type    = string
}

output "vm_name" {
  value = var.vm_name_input
}

output "public_ip" {
  value = google_compute_instance.vm-instance.network_interface[0].access_config[0].nat_ip
}
