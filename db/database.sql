drop table papers;

create table papers
( id serial primary key
 ,title varchar(200)
 ,author varchar(64)
 ,annotation text
 ,paper_text text
 ,url text UNIQUE not Null
 ,type varchar
);

create or replace function pInsert(nTitle text, nAuthor text, nAnnotation text, nUrl text, nPaper_text text)
returns boolean
as $$
begin

	if not exists(select url from papers where url = nUrl ) then

			insert into papers(title, author, annotation, paper_text, url) values(nTitle, nAuthor, nAnnotation, nPaper_text, nUrl);
			return true;
	end if;
	return false;
end;
$$ Language plpgsql;