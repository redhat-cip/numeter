from django.db import models

class Host(models.Model):
	ID = models.CharField(max_length=300, db_column="hostid")
	HostIDFiltredName = models.CharField(max_length=300)
	HostIDHash = models.CharField(max_length=300)
	Address = models.CharField(max_length=300, db_column='Addr')
	address = models.CharField(max_length=300)
	Name = models.CharField(max_length=300)
	Plugin = models.CharField(max_length=300)
	Description = models.CharField(max_length=300)
	
	def get_info(self):
		return {
			'ID': self.ID,
			'HostIDFiltredName': self.HostIDFiltredName,
			'HostIDHash': self.HostIDHash,
			'Address': self.Address,
			'address': self.address,
			'Name': self.Name,
			'Plugin': self.Plugin,
			'Description': self.Description,
		}

